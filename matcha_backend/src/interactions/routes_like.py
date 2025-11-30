import os
import sys
import logging

from flask import Blueprint, flash, request, jsonify, current_app, g, send_file, url_for
from werkzeug.exceptions import BadRequestKeyError
from flask_socketio import emit, join_room, leave_room


sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))

from database.crud.matching_operations_crud import Matching
from database.crud.user_crud import User
from database.crud.profile_crud import Profile
from database.crud.interactions_crud import Interactions
from database.crud.notification_crud import Notification

from utils.validate_profile_data import validate_profile_data
from utils.security import auth_guard
from utils.fame_rating import calculate_fame_rating
from utils.manage_interactions import ManageInteractions
from utils.image_handler import upload_pictures
from utils.notification_service import NotificationService
from src.interactions import interactions_bp




@interactions_bp.route("/like/<username>", methods=["POST"])
@auth_guard
def like_user_by_username(username):
    '''Simplified endpoint to like a user by username.
    This is a convenience wrapper around like_dislike for frontend compatibility.
    '''
    try:
        # Validate username parameter
        if not username or username.strip() == "":
            return jsonify({"error": "Username is required"}), 400
        
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        # Check if acting user has a profile picture
        profile_crud = Profile(connection_pool)
        profile = profile_crud.get_profile_by_user_id(g.user_id)
        logger = logging.getLogger(__name__)
        
        if not profile or not profile.get("profile_picture"):
            return jsonify({"error": "You need a profile picture to like other users"}), 409
        
        user_crud = User(connection_pool)
        
        # Prevent users from liking themselves
        current_username = user_crud.get_user_by('id', g.user_id, 'username')
        if username == current_username.get('username'):
            return jsonify({"error": "You cannot like yourself"}), 409
        
        # Check if the liked user exists
        liked_user_data = user_crud.get_user_by_username(username=username)
        if not liked_user_data:
            return jsonify({"error": f"User '{username}' does not exist"}), 404
        
        # Check if the liked user has a profile
        liked_user_profile = profile_crud.get_profile_by_user_id(liked_user_data["id"])
        if not liked_user_profile:
            return jsonify({"error": "This user does not have a profile yet"}), 409
        
        # Initialize interaction services
        interactions_crud = Interactions(connection_pool, g.user_id, liked_user_data["id"])
        manage_interactions = ManageInteractions(connection_pool, interactions_crud)
        
        # Determine the action (like or match)
        action = manage_interactions.check_action(g.user_id, liked_user_data["id"])
        notification_service = NotificationService(connection_pool)

        if action == "like" or action == "match":
            # Register the like
            interactions_crud.like_user()
            
            # Send notification
            notification_service.create_notification(
                user_id=liked_user_data["id"],
                notification_type="like" if action == "like" else "match",
                reference_id=g.user_id,
            )
            
            # Update fame rating
            new_rating = calculate_fame_rating(liked_user_profile['fame_rating'], type='like')
            profile_crud.update_fame_rating(liked_user_data["id"], new_rating)
            
            # Handle match - increment match count for both users
            if action == "match":
                # Increment matches_count for both users
                current_profile = profile_crud.get_profile_by_user_id(g.user_id)
                if current_profile:
                    new_count = current_profile.get('matches_count', 0) + 1
                    profile_crud.update(
                        'profiles',
                        {'matches_count': new_count},
                        where='user_id = %s',
                        where_params=(g.user_id,)
                    )
                
                if liked_user_profile:
                    new_count = liked_user_profile.get('matches_count', 0) + 1
                    profile_crud.update(
                        'profiles',
                        {'matches_count': new_count},
                        where='user_id = %s',
                        where_params=(liked_user_data["id"],)
                    )
                
                # Send real-time notification via Socket.IO
                try:
                    socketio = current_app.config.get("SOCKETIO")
                    if socketio:
                        # Notify both users about the match
                        socketio.emit("new_match", {
                            "matched_with": liked_user_data["username"],
                            "user_id": liked_user_data["id"],
                            "message": f"You matched with {liked_user_data['username']}! 🎉"
                        }, room=f"user_{g.user_id}")
                        
                        socketio.emit("new_match", {
                            "matched_with": current_username.get('username'),
                            "user_id": g.user_id,
                            "message": f"You matched with {current_username.get('username')}! 🎉"
                        }, room=f"user_{liked_user_data['id']}")
                        
                        logger.info(f"✅ Match notification sent to both users")
                except Exception as socket_error:
                    logger.error(f"Failed to send Socket.IO match notification: {socket_error}")
            
            return jsonify({
                "status": "success",
                "action": action,
                "message": f"It's a match! 🎉" if action == "match" else f"You liked {username} 💖",
                "new_fame_rating": new_rating,
                "is_match": action == "match"
            }), 200
        
        elif action == "dislike":
            # This endpoint is for liking only, but handle the case
            interactions_crud.dislike_user()
            notification_service.create_notification(
                user_id=liked_user_data["id"],
                notification_type="dislike",
                reference_id=g.user_id,
            )
            new_rating = calculate_fame_rating(liked_user_profile['fame_rating'], type='dislike')
            profile_crud.update_fame_rating(liked_user_data["id"], new_rating)
            
            return jsonify({
                "status": "success",
                "action": "dislike",
                "message": f"You disliked {username}",
                "new_fame_rating": new_rating
            }), 200
            
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error in like_user_by_username for {username}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": f"Failed to like user: {str(e)}"}), 500


@interactions_bp.route("/like_dislike", methods=["POST"])
@auth_guard
def like_dislike():
    '''Endpoint to like or dislike a user.
    Expects JSON body with key 'liked_user' containing the username of the user to like or dislike.
    '''
    try:
        requested_data = request.json
        # Ensure the request contains the 'liked_user' key
        if "liked_user" not in requested_data:
            return jsonify({"error": "Key error: request must include 'liked_user' with the liked user's username"}), 400
        
        connection_pool = current_app.config["CONNECTION_POOL"]
        # Check if the database connection pool is available
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        # Ensure the acting user has a profile picture before they can like/dislike others
        profile_crud = Profile(connection_pool)
        profile = profile_crud.get_profile_by_user_id(g.user_id)
        logger = logging.getLogger(__name__)
        if not profile["profile_picture"]:
            return jsonify({"error": "You need profile picture to complete this action"}), 409
        
        user_crud = User(connection_pool)
        
        # Prevent users from liking/disliking themselves
        current_user_data = user_crud.get_user_by('id', g.user_id, 'username')
        current_username = current_user_data.get('username') if current_user_data else None
        
        if not current_username:
            return jsonify({"error": "Current user not found"}), 404
            
        if requested_data["liked_user"] == current_username:
            return jsonify({"error": "You cannot like or dislike yourself"}), 409
        
        # Check if the liked user exists in the database
        liked_user_data = user_crud.get_user_by_username(username=requested_data["liked_user"])
        if not liked_user_data:
            return jsonify({"error": "liked user does not exist"}), 409
        
        # Check if the liked user has a profile
        liked_user_profile = profile_crud.get_profile_by_user_id(liked_user_data["id"])
        if not liked_user_profile:
            return jsonify({"error": "The user you are trying to like/dislike does not have a profile"}), 409
        
        # Initialize interaction and notification services
        interactions_crud = Interactions(connection_pool, g.user_id, liked_user_data["id"])
        manage_interactions = ManageInteractions(connection_pool, interactions_crud)
        # Determine the action (like, dislike, or match)
        action = manage_interactions.check_action(g.user_id, liked_user_data["id"])
        notification_service = NotificationService(connection_pool)

        if action == "like" or action == "match":
            # Register the like and send notification (like or match)
            interactions_crud.like_user()
            notification_service.create_notification(
                user_id=liked_user_data["id"],
                notification_type="like" if action == "like" else "match",
                reference_id=g.user_id,
            )
            # Update the liked user's fame rating
            new_rating = calculate_fame_rating(liked_user_profile['fame_rating'], type='like')
            profile_crud.update_fame_rating(liked_user_data["id"], new_rating)
            
            # Handle match - increment match count for both users
            if action == "match":
                # Increment matches_count for both users
                current_profile = profile_crud.get_profile_by_user_id(g.user_id)
                if current_profile:
                    new_count = current_profile.get('matches_count', 0) + 1
                    profile_crud.update(
                        'profiles',
                        {'matches_count': new_count},
                        where='user_id = %s',
                        where_params=(g.user_id,)
                    )
                
                if liked_user_profile:
                    new_count = liked_user_profile.get('matches_count', 0) + 1
                    profile_crud.update(
                        'profiles',
                        {'matches_count': new_count},
                        where='user_id = %s',
                        where_params=(liked_user_data["id"],)
                    )
                
                # Send real-time notification via Socket.IO
                try:
                    socketio = current_app.config.get("SOCKETIO")
                    if socketio:
                        # Notify both users about the match
                        socketio.emit("new_match", {
                            "matched_with": liked_user_data["username"],
                            "user_id": liked_user_data["id"],
                            "message": f"You matched with {liked_user_data['username']}! 🎉"
                        }, room=f"user_{g.user_id}")
                        
                        socketio.emit("new_match", {
                            "matched_with": current_username,
                            "user_id": g.user_id,
                            "message": f"You matched with {current_username}! 🎉"
                        }, room=f"user_{liked_user_data['id']}")
                        
                        logger.info(f"✅ Match notification sent to both users")
                except Exception as socket_error:
                    logger.error(f"Failed to send Socket.IO match notification: {socket_error}")

        elif action == "dislike":
            # Send dislike notification and register the dislike
            notification_service.create_notification(
                user_id=liked_user_data["id"],
                notification_type="dislike",
                reference_id=g.user_id,
            )
            interactions_crud.dislike_user()
            # Update the liked user's fame rating
            new_rating = calculate_fame_rating(liked_user_profile['fame_rating'], type='dislike')
            profile_crud.update_fame_rating(liked_user_data["id"], new_rating)
            # room = f"chat_{min(g.user_id, liked_user_data["id"])}_{max(g.user_id, liked_user_data['id'])}"
            # leave_room(room)
            # emit("room_leaved",
            #      {
            #          "room": room,
            #          "users": [username, liked_user_data["username"]]
            #      },
            #      room=room 
            #     )

        # Return success response with the action and new fame rating
        return jsonify({"status": "ok",
                        "message": f"user has {action} {requested_data['liked_user']}",
                        "new_fame_rating": new_rating}), 201
    except Exception as e:
        # Handle unexpected errors
        logger = logging.getLogger(__name__)
        logger.error(f"Error in like_dislike: {str(e)}")
        return jsonify({"error": str(e)}), 400



@interactions_bp.route("/get_users/<interaction_type>")
@auth_guard
def get_user_likes(interaction_type):
    '''Endpoint to get users that the current user has liked or users that have liked the current user.
    interaction_type must be either 'liked' or 'likers'.
    '''
    try:
        if interaction_type not in ["liked", "likers"]:
            return jsonify({"error": "Interaction type undifined it \
                must be either <liked> to see what the user liked \
                    or <likers> to see who liked the user"})
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        interactions_crud = Interactions(connection_pool, g.user_id, None)
        user_crud = User(connection_pool)
        if interaction_type == "liked":
            user_ids = interactions_crud.get_user_likes()
        else:
            user_ids = interactions_crud.get_user_likers()

        usernames = []
        for user_id in user_ids:
            user_data = user_crud.get_user_by('id', user_id, "username")
            if user_data and 'username' in user_data:
                usernames.append(user_data['username'])
        
        return jsonify({"result": usernames}), 200
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error in get_user_likes: {str(e)}")
        return jsonify({"error": str(e)}), 400


@interactions_bp.route("/is_matched", methods=["POST"])
@auth_guard
def is_matched():
    '''Endpoint to check if the logged in user is matched with another user.
    Expects JSON body with key 'other_user' containing the username of the other user.
    '''
    logger = logging.getLogger(__name__)
    try:
        # Validate request body
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
            
        requested_data = request.get_json()
        if not requested_data:
            return jsonify({"error": "Request body is required"}), 400
            
        if "other_user" not in requested_data:
            return jsonify({"error": "Key error: request must include 'other_user' with the other user's username"}), 400
        
        other_username = requested_data["other_user"]
        if not other_username or not isinstance(other_username, str):
            return jsonify({"error": "Invalid 'other_user' value - must be a non-empty string"}), 400
        
        connection_pool = current_app.config.get("CONNECTION_POOL")
        if not connection_pool:
            logger.error("Database connection pool is not available")
            return jsonify({"error": "Database connection pool is not available"}), 500

        user_crud = User(connection_pool)
        
        # Ensure the acting user is not trying to check match status with themselves
        current_user_data = user_crud.get_user_by('id', g.user_id, 'username')
        if not current_user_data or 'username' not in current_user_data:
            logger.error(f"Current user {g.user_id} not found")
            return jsonify({"error": "Current user not found"}), 404
            
        current_username = current_user_data['username']
        
        if other_username == current_username:
            return jsonify({"error": "You cannot check match status with yourself"}), 400
        
        # Check if the other user exists
        other_user_data = user_crud.get_user_by_username(username=other_username)
        if not other_user_data:
            logger.warning(f"User '{other_username}' not found")
            return jsonify({"error": "The specified user does not exist"}), 404
        
        if 'id' not in other_user_data:
            logger.error(f"User data for '{other_username}' is missing 'id' field")
            return jsonify({"error": "Invalid user data"}), 500
        
        # Check match status
        matching_crud = Matching(connection_pool)
        matched_users_ids = matching_crud.get_matched_users(g.user_id)
        is_matched = matched_users_ids and other_user_data["id"] in matched_users_ids
        
        # NOTE: Removed connect_users() call - this endpoint should ONLY check match status,
        # not create matches. Matches are created when users like each other via /like endpoint.

        return jsonify({"result": is_matched}), 200
        
    except KeyError as e:
        logger.error(f"KeyError in is_matched: {str(e)}")
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except ValueError as e:
        logger.error(f"ValueError in is_matched: {str(e)}")
        return jsonify({"error": f"Invalid value: {str(e)}"}), 400
    except Exception as e:
        logger.exception(f"Unexpected error in is_matched")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500


@interactions_bp.route("/who_liked_me", methods=["GET"])
@auth_guard
def who_liked_me():
    '''Get all users who liked the current user'''
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        
        interactions_crud = Interactions(connection_pool, g.user_id, None)
        user_crud = User(connection_pool)
        profile_crud = Profile(connection_pool)
        
        # Get user IDs who liked this user
        liker_ids = interactions_crud.get_user_likers()
        
        # Build detailed user list
        likers = []
        for user_id in liker_ids:
            user_data = user_crud.get_user_by('id', user_id, '*')
            if user_data and 'id' in user_data:
                profile = profile_crud.get_profile_by_user_id(user_id)
                likers.append({
                    "id": user_id,
                    "username": user_data.get("username"),
                    "first_name": user_data.get("first_name"),
                    "last_name": user_data.get("last_name"),
                    "profile_picture": profile.get("profile_picture") if profile else None,
                    "age": profile.get("age") if profile else None,
                })
        
        return jsonify({"result": likers}), 200
        
    except Exception as e:
        logging.exception("Error in who_liked_me")
        return jsonify({"error": str(e)}), 500


@interactions_bp.route("/my_connections", methods=["GET"])
@auth_guard
def my_connections():
    '''Get all matched users (mutual likes)'''
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        
        matching_crud = Matching(connection_pool)
        user_crud = User(connection_pool)
        profile_crud = Profile(connection_pool)
        
        # Get matched user IDs
        matched_user_ids = matching_crud.get_matched_users(g.user_id)
        
        # Build detailed user list and filter out blocked users
        connections = []
        if matched_user_ids:
            for user_id in matched_user_ids:
                # Check if blocked (both directions)
                interactions_check = Interactions(connection_pool, g.user_id, user_id)
                if interactions_check.is_blocked() or interactions_check.did_i_block():
                    continue  # Skip blocked users
                
                user_data = user_crud.get_user_by('id', user_id, '*')
                if user_data and 'id' in user_data:
                    profile = profile_crud.get_profile_by_user_id(user_id)
                    connections.append({
                        "id": user_id,
                        "username": user_data.get("username"),
                        "first_name": user_data.get("first_name"),
                        "last_name": user_data.get("last_name"),
                        "profile_picture": profile.get("profile_picture") if profile else None,
                        "age": profile.get("age") if profile else None,
                    })
        
        return jsonify({"result": connections}), 200
        
    except Exception as e:
        logging.exception("Error in my_connections")
        return jsonify({"error": str(e)}), 500


@interactions_bp.route("/unlike/<username>", methods=["DELETE"])
@auth_guard
def unlike_user(username):
    '''Unlike a user and remove all associations (match, conversation, etc.)'''
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        
        logger = logging.getLogger(__name__)
        user_crud = User(connection_pool)
        
        # Get current user info
        current_user_data = user_crud.get_user_by('id', g.user_id, 'username')
        current_username = current_user_data.get('username') if current_user_data else None
        
        if not current_username:
            return jsonify({"error": "Current user not found"}), 404
        
        # Prevent users from unliking themselves
        if username == current_username:
            return jsonify({"error": "You cannot unlike yourself"}), 409
        
        # Check if the user to unlike exists
        unliked_user_data = user_crud.get_user_by_username(username=username)
        if not unliked_user_data:
            return jsonify({"error": f"User '{username}' does not exist"}), 404
        
        unliked_user_id = unliked_user_data["id"]
        
        # Initialize CRUD services
        interactions_crud = Interactions(connection_pool, g.user_id, unliked_user_id)
        matching_crud = Matching(connection_pool)
        profile_crud = Profile(connection_pool)
        notification_service = NotificationService(connection_pool)
        
        # Check if user had previously liked this person
        user_likes = interactions_crud.get_user_likes(g.user_id)
        if unliked_user_id not in user_likes:
            return jsonify({"error": "You haven't liked this user"}), 409
        
        # Check if they were matched
        was_matched = matching_crud.are_matched(g.user_id, unliked_user_id)
        
        # Remove the like from database
        interactions_crud.dislike_user()
        logger.info(f"User {g.user_id} unliked user {unliked_user_id}")
        
        # If they were matched, remove the match
        if was_matched:
            matching_crud.unmatche(g.user_id, unliked_user_id)
            logger.info(f"Match removed between {g.user_id} and {unliked_user_id}")
            
            # Decrement matches_count for both users
            current_profile = profile_crud.get_profile_by_user_id(g.user_id)
            unliked_profile = profile_crud.get_profile_by_user_id(unliked_user_id)
            
            if current_profile:
                new_count = max(0, current_profile.get('matches_count', 0) - 1)
                profile_crud.update(
                    'profiles',
                    {'matches_count': new_count},
                    where='user_id = %s',
                    where_params=(g.user_id,)
                )
            
            if unliked_profile:
                new_count = max(0, unliked_profile.get('matches_count', 0) - 1)
                profile_crud.update(
                    'profiles',
                    {'matches_count': new_count},
                    where='user_id = %s',
                    where_params=(unliked_user_id,)
                )
            
            # Delete conversation and messages
            try:
                from database.crud.chat_crud import Chat
                chat_crud = Chat(connection_pool)
                
                # Get conversation ID
                user_a = min(g.user_id, unliked_user_id)
                user_b = max(g.user_id, unliked_user_id)
                
                query = """
                    SELECT conversation_id FROM conversations
                    WHERE user1_id = %s AND user2_id = %s
                """
                conv_result = chat_crud.execute(query, (user_a, user_b), fetch=True)
                
                if conv_result and len(conv_result) > 0:
                    conversation_id = conv_result[0]['conversation_id']
                    
                    # Delete all messages in the conversation
                    chat_crud.delete(
                        'messages',
                        where='conversation_id = %s',
                        where_params=(conversation_id,)
                    )
                    
                    # Delete the conversation
                    chat_crud.delete(
                        'conversations',
                        where='conversation_id = %s',
                        where_params=(conversation_id,)
                    )
                    
                    logger.info(f"Deleted conversation {conversation_id} and all messages")
            except Exception as conv_error:
                logger.error(f"Error deleting conversation: {conv_error}")
        
        # Update fame rating for unliked user (decrease)
        unliked_profile = profile_crud.get_profile_by_user_id(unliked_user_id)
        if unliked_profile:
            new_rating = calculate_fame_rating(unliked_profile['fame_rating'], type='dislike')
            profile_crud.update_fame_rating(unliked_user_id, new_rating)
        
        # Send "unliked" notification to the other user
        notification_service.create_notification(
            user_id=unliked_user_id,
            notification_type="unliked",
            reference_id=g.user_id,
        )
        
        # Send real-time notification via Socket.IO
        try:
            socketio = current_app.config.get("SOCKETIO")
            if socketio:
                socketio.emit("unliked", {
                    "unliked_by": current_username,
                    "user_id": g.user_id,
                    "message": f"{current_username} unliked you",
                    "was_matched": was_matched
                }, room=f"user_{unliked_user_id}")
                logger.info(f"✅ Unlike notification sent to user {unliked_user_id}")
        except Exception as socket_error:
            logger.error(f"Failed to send Socket.IO unlike notification: {socket_error}")
        
        return jsonify({
            "status": "success",
            "message": f"You unliked {username}",
            "was_matched": was_matched
        }), 200
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error in unlike_user for {username}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": f"Failed to unlike user: {str(e)}"}), 500


@interactions_bp.route("/disconnect/<username>", methods=["DELETE"])
@auth_guard
def disconnect_from_match(username):
    '''Disconnect from a matched user. This is an alias for unlike that's more semantically clear for matched users.'''
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        
        logger = logging.getLogger(__name__)
        user_crud = User(connection_pool)
        
        # Get the user to disconnect from
        disconnected_user_data = user_crud.get_user_by_username(username=username)
        if not disconnected_user_data:
            return jsonify({"error": f"User '{username}' does not exist"}), 404
        
        disconnected_user_id = disconnected_user_data["id"]
        
        # Initialize services
        matching_crud = Matching(connection_pool)
        
        # Verify they are actually matched
        if not matching_crud.are_matched(g.user_id, disconnected_user_id):
            return jsonify({"error": "You are not connected with this user"}), 409
        
        # Use the unlike_user function to handle all the disconnection logic
        return unlike_user(username)
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error in disconnect_from_match for {username}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": f"Failed to disconnect from user: {str(e)}"}), 500