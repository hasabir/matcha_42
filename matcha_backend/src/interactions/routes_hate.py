import os
import sys
import logging

from flask import Blueprint, flash, request, jsonify, current_app, g, send_file, url_for
from werkzeug.exceptions import BadRequestKeyError

from database.crud.matching_operations_crud import Matching
from database.crud.user_crud import User
from utils.fame_rating import calculate_fame_rating

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))

from database.crud.profile_crud import Profile
from database.crud.interactions_crud import Interactions
from utils.security import auth_guard
from utils.notification_service import NotificationService
from src.interactions import interactions_bp



@interactions_bp.route("/block", methods=["POST"])
@auth_guard
def block_user():
    """
    Endpoint to block a user.
    Expects JSON body with key 'blocked_user' containing the username of the user to block.
    """
    try:
        requested_data = request.get_json()
        if not requested_data:
            return jsonify({"error": "Request body must be JSON"}), 400
        if not isinstance(requested_data, dict):
            return jsonify({"error": "Request body must be a JSON object"}), 400
        if "blocked_user" not in requested_data:
            return jsonify({"error": "Request body must contain 'blocked_user' key"}), 400

        connection_pool = current_app.config.get("CONNECTION_POOL")
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        user_crud = User(connection_pool)
        
        # Ensure the acting user is not trying to block themselves
        current_user_data = user_crud.get_user_by('id', g.user_id, 'username')
        current_username = current_user_data.get('username') if current_user_data else None
        
        if not current_username:
            return jsonify({"error": "Current user not found"}), 404
            
        if requested_data["blocked_user"] == current_username:
            return jsonify({"error": "You cannot block yourself"}), 409

        # Check if the blocked user exists
        blocked_user_data = user_crud.get_user_by_username(username=requested_data["blocked_user"])
        if not blocked_user_data:
            return jsonify({"error": "Blocked user does not exist"}), 409
        
        interactions_crud = Interactions(connection_pool, g.user_id, blocked_user_data["id"])
        # Check if I already blocked them (not if they blocked me)
        if interactions_crud.did_i_block():
            return jsonify({"error": f"You have already blocked user {requested_data['blocked_user']}"}), 409
        
        matching_crud = Matching(connection_pool)
        # Remove match if exists
        if matching_crud.are_matched(g.user_id, blocked_user_data["id"]):
            matching_crud.unmatche(g.user_id, blocked_user_data["id"])
            logger = logging.getLogger(__name__)
            logger.info(f"User {g.user_id} blocked {blocked_user_data['id']} - match removed")
        
        # Remove likes from both directions
        interactions_crud.dislike_user()  # Remove my like
        
        # Create a temporary interaction object to remove their like to me
        temp_interactions = Interactions(connection_pool, blocked_user_data["id"], g.user_id)
        temp_interactions.dislike_user()  # Remove their like
        
        # Finally, block the user
        interactions_crud.block_user()
        profile_crud = Profile(connection_pool)
        blocked_user_profile = profile_crud.get_profile_by_user_id(blocked_user_data["id"])
        new_rating = calculate_fame_rating(blocked_user_profile['fame_rating'], type='block')  
        profile_crud.update_fame_rating(blocked_user_data["id"], new_rating)
        
        notification_service = NotificationService(connection_pool)
    
        notification_service.create_notification(
            user_id=blocked_user_data["id"],
            notification_type="block",
            reference_id=g.user_id,
        )
        
        # Send real-time Socket.IO notification to both users to update their UI
        try:
            socketio = current_app.config.get("SOCKETIO")
            if socketio:
                logger = logging.getLogger(__name__)
                # Notify the blocker to update their matches list
                socketio.emit("user_blocked", {
                    "blocked_user_id": blocked_user_data["id"],
                    "blocked_username": requested_data["blocked_user"],
                    "message": f"You blocked {requested_data['blocked_user']}"
                }, room=f"user_{g.user_id}")
                
                # Notify the blocked user to update their matches list
                socketio.emit("user_blocked_by", {
                    "blocker_user_id": g.user_id,
                    "blocker_username": current_username,
                    "message": "A user has blocked you"
                }, room=f"user_{blocked_user_data['id']}")
                
                logger.info(f"✅ Block notifications sent via Socket.IO")
        except Exception as socket_error:
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send Socket.IO block notification: {socket_error}")
        
        
        return jsonify({"status": "ok", "message": f"you blocked user {requested_data['blocked_user']}"}), 200
    except Exception as e:
        logging.exception("Error blocking user")
        return jsonify({"error": str(e)}), 409
    
    
@interactions_bp.route("/unblock", methods=["POST"])
@auth_guard
def unblock_user():
    ''' Endpoint to unblock a user.
    Expects JSON body with key 'unblocked_user' containing the username of the user to unblock.
    '''
    try:
        requested_data = request.get_json()
        if not requested_data:
            return jsonify({"error": "Request body must be JSON"}), 400
        if not isinstance(requested_data, dict):
            return jsonify({"error": "Request body must be a JSON object"}), 400
        if "unblocked_user" not in requested_data:
            return jsonify({"error": "Request body must contain 'unblocked_user' key"}), 400

        connection_pool = current_app.config.get("CONNECTION_POOL")
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        user_crud = User(connection_pool)
        # Ensure the acting user is not trying to unblock themselves
        current_user_data = user_crud.get_user_by('id', g.user_id, 'username')
        current_username = current_user_data.get('username') if current_user_data else None
        
        if not current_username:
            return jsonify({"error": "Current user not found"}), 404
            
        if requested_data["unblocked_user"] == current_username:
            return jsonify({"error": "You cannot unblock yourself"}), 409

        # Check if the unblocked user exists
        unblocked_user_data = user_crud.get_user_by_username(username=requested_data["unblocked_user"])
        if not unblocked_user_data:
            return jsonify({"error": "Unblocked user does not exist"}), 409
        
        interactions_crud = Interactions(connection_pool, g.user_id, unblocked_user_data["id"])
        if not interactions_crud.did_i_block():
            return jsonify({"error": f"You have not blocked user {requested_data['unblocked_user']}"}), 409


        interactions_crud.unblock_user()
        profile_crud = Profile(connection_pool)
        unblocked_user_profile = profile_crud.get_profile_by_user_id(unblocked_user_data["id"])
        new_rating = calculate_fame_rating(unblocked_user_profile['fame_rating'], type='unblock')  
        profile_crud.update_fame_rating(unblocked_user_data["id"], new_rating)
        return jsonify({"status": "ok", "message": f"you unblocked user {requested_data['unblocked_user']}"}), 200
    except Exception as e:
        logging.exception("Error unblocking user")
        return jsonify({"error": str(e)}), 409
    
@interactions_bp.route("/report", methods=["POST"])
@auth_guard
def report_user():
    ''' Endpoint to report a user.
    Expects JSON body with key 'reported_user' containing the username of the user to report.
    '''
    try:
        requested_data = request.get_json()
        if not requested_data:
            return jsonify({"error": "Request body must be JSON"}), 400
        if not isinstance(requested_data, dict):
            return jsonify({"error": "Request body must be a JSON object"}), 400
        if "reported_user" not in requested_data:
            return jsonify({"error": "Request body must contain 'reported_user' key"}), 400

        connection_pool = current_app.config.get("CONNECTION_POOL")
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        user_crud = User(connection_pool)
        # Ensure the acting user is not trying to report themselves
        current_user_data = user_crud.get_user_by('id', g.user_id, 'username')
        current_username = current_user_data.get('username') if current_user_data else None
        
        if not current_username:
            return jsonify({"error": "Current user not found"}), 404
            
        if requested_data["reported_user"] == current_username:
            return jsonify({"error": "You cannot report yourself"}), 409

        # Check if the reported user exists
        reported_user_data = user_crud.get_user_by_username(username=requested_data["reported_user"])
        if not reported_user_data:
            return jsonify({"error": "Reported user does not exist"}), 409
        
        interactions_crud = Interactions(connection_pool, g.user_id, reported_user_data["id"])
        if interactions_crud.has_reported():
            #TODO: limit number of reports per user?
            
            return jsonify({"error": f"You have already reported user {requested_data['reported_user']}"}), 409
        
        #TODO fame rating decrease? or other action?
        
        interactions_crud.report_user()
        
        # Get profile data to update fame rating
        profile_crud = Profile(connection_pool)
        reported_user_id = reported_user_data["id"]  # Store the user ID before overwriting
        reported_profile = profile_crud.get_profile_by_user_id(reported_user_id)
        
        if reported_profile:
            new_rating = calculate_fame_rating(reported_profile['fame_rating'], type='report')  
            profile_crud.update_fame_rating(reported_user_id, new_rating)
        
        return jsonify({"status": "ok", "message": f"you reported user {requested_data['reported_user']}"}), 200
    except Exception as e:
        logging.exception("Error reporting user")
        return jsonify({"error": str(e)}), 409


@interactions_bp.route("/check_block_status/<username>", methods=["GET"])
@auth_guard
def check_block_status(username):
    """
    Check if a user is blocked (either direction).
    Returns block status without making a full profile request.
    """
    try:
        connection_pool = current_app.config.get("CONNECTION_POOL")
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        user_crud = User(connection_pool)
        other_user_data = user_crud.get_user_by_username(username=username)
        
        if not other_user_data:
            return jsonify({"error": "User not found"}), 404
        
        interactions_crud = Interactions(connection_pool, g.user_id, other_user_data["id"])
        
        is_blocked_by_them = interactions_crud.is_blocked()
        did_i_block_them = interactions_crud.did_i_block()
        is_blocked = is_blocked_by_them or did_i_block_them
        
        return jsonify({
            "is_blocked": is_blocked,
            "blocked_by_them": is_blocked_by_them,
            "blocked_by_me": did_i_block_them,
            "message": "You are blocked by this user" if is_blocked_by_them else ("You have blocked this user" if did_i_block_them else None)
        }), 200
        
    except Exception as e:
        logging.exception("Error checking block status")
        return jsonify({"error": str(e)}), 500
    
    
     