import os
import sys
import logging

from flask import Blueprint, flash, request, jsonify, current_app, g, send_file, url_for
from werkzeug.exceptions import BadRequestKeyError

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))

from database.crud.matching_operations_crud import Matching
from database.crud.user_crud import User
from database.crud.profile_crud import Profile
from database.crud.interactions_crud import Interactions
from utils.validate_profile_data import validate_profile_data
from utils.security import auth_guard
from utils.fame_rating import calculate_fame_rating
from utils.manage_interactions import ManageInteractions
from utils.image_handler import upload_pictures
from src.interactions import interactions_bp



@interactions_bp.route("/like_dislike", methods=["POST"])
@auth_guard
def like_dislike():
    '''Endpoint to like or dislike a user.
    Expects JSON body with key 'liked_user' containing the username of the user to like or dislike.
    '''
    try:
        requested_data = request.json
        if "liked_user" not in requested_data:
            return jsonify({"error": "Key error: request must include 'liked_user' with the liked user's username"}), 400
        
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        # Ensure the acting user has a profile picture before they can like/dislike others
        profile_crud = Profile(connection_pool)
        profile = profile_crud.get_profile_by_user_id(g.user_id)
        logger = logging.getLogger(__name__)
        if not profile["profile_picture"]:
            return jsonify({"error": "You need profile picture to complete this action"}), 409
        
        user_crud = User(connection_pool)
        
        # Ensure the acting user is not trying to like/dislike themselves
        username = user_crud.get_user_by('id', g.user_id, 'username')
        if requested_data["liked_user"] == username:
            return jsonify({"error": "You cannot like or dislike yourself"}), 409
        
        # Check if the liked user exists
        liked_user_data = user_crud.get_user_by_username(username=requested_data["liked_user"])
        if not liked_user_data:
            return jsonify({"error": "liked user does not exist"}), 409
        
        # Check if the liked user has a profile
        liked_user_profile = profile_crud.get_profile_by_user_id(liked_user_data["id"])
        if not liked_user_profile:
            return jsonify({"error": "The user you are trying to like/dislike does not have a profile"}), 409
        
        interactions_crud = Interactions(connection_pool, g.user_id, liked_user_data["id"])
        manage_interactions = ManageInteractions(connection_pool, interactions_crud)
        action = manage_interactions.check_action(g.user_id, liked_user_data["id"])
        if action == "like":
            interactions_crud.like_user()
            new_rating = calculate_fame_rating(liked_user_profile['fame_rating'], type='like')
            profile_crud.update_fame_rating(liked_user_data["id"], new_rating)

        elif action == "dislike":
            interactions_crud.dislike_user()
            new_rating = calculate_fame_rating(liked_user_profile['fame_rating'], type='dislike')
            profile_crud.update_fame_rating(liked_user_data["id"], new_rating)
        return jsonify({"status": "ok",
                        "message": f"user has {action} {requested_data["liked_user"]}",
                        "new_fame_rating": new_rating}), 201
    except Exception as e:
        return jsonify({"error": e}), 400



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
            username = user_crud.get_user_by('id', user_id, "username")
            usernames.append(username)
        
        return jsonify({"result": usernames}), 200
        
    except Exception as e:
        return jsonify({"error": e})


@interactions_bp.route("/is_matched", methods=["POST"])
@auth_guard
def is_matched():
    '''Endpoint to check if the logged in user is matched with another user.
    Expects JSON body with key 'other_user' containing the username of the other user.
    '''
    try:
        requested_data = request.json
        if "other_user" not in requested_data:
            return jsonify({"error": "Key error: request must include 'other_user' with the other user's username"}), 400
        
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        user_crud = User(connection_pool)
        
        # Ensure the acting user is not trying to check match status with themselves
        username = user_crud.get_user_by('id', g.user_id, 'username')
        if requested_data["other_user"] == username:
            return jsonify({"error": "You cannot check match status with yourself"}), 409
        
        # Check if the other user exists
        other_user_data = user_crud.get_user_by_username(username=requested_data["other_user"])
        if not other_user_data:
            return jsonify({"error": "The specified user does not exist"}), 409
        
        matching_crud = Matching(connection_pool)
        matched_users_ids = matching_crud.get_matched_users(g.user_id)
        is_matched = matched_users_ids and other_user_data["id"] in matched_users_ids
        
        manage_interactions = ManageInteractions(connection_pool, None)
        test = manage_interactions.connect_users(g.user_id, other_user_data["id"])
        return jsonify({"result": is_matched, "test": test}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400