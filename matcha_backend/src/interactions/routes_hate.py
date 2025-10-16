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
        username = user_crud.get_user_by('id', g.user_id, 'username')
        if requested_data["blocked_user"] == username:
            return jsonify({"error": "You cannot block yourself"}), 409

        # Check if the blocked user exists
        blocked_user_data = user_crud.get_user_by_username(username=requested_data["blocked_user"])
        if not blocked_user_data:
            return jsonify({"error": "Blocked user does not exist"}), 409
        
        interactions_crud = Interactions(connection_pool, g.user_id, blocked_user_data["id"])
        if interactions_crud.is_blocked():
            return jsonify({"error": f"You have already blocked user {requested_data['blocked_user']}"}), 409
        
        matching_crud = Matching(connection_pool)
        if matching_crud.are_matched(g.user_id, blocked_user_data["id"]):
            matching_crud.unmatche(g.user_id, blocked_user_data["id"])
        interactions_crud.dislike_user()
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
        
        
        return jsonify({"status": "ok", "message": f"you blocked user {requested_data["blocked_user"]}"}), 200
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
        username = user_crud.get_user_by('id', g.user_id, 'username')
        if requested_data["unblocked_user"] == username:
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
        username = user_crud.get_user_by('id', g.user_id, 'username')
        if requested_data["reported_user"] == username:
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
        profile_crud = Profile(connection_pool)
        reported_user_data = profile_crud.get_profile_by_user_id(reported_user_data["id"])
        new_rating = calculate_fame_rating(reported_user_data['fame_rating'], type='report')  
        profile_crud.update_fame_rating(reported_user_data["id"], new_rating)
        
        return jsonify({"status": "ok", "message": f"you reported user {requested_data['reported_user']}"}), 200
    except Exception as e:
        logging.exception("Error reporting user")
        return jsonify({"error": str(e)}), 409
    
    
    