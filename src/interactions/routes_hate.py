import os
import sys
import logging

from flask import Blueprint, flash, request, jsonify, current_app, g, send_file, url_for
from werkzeug.exceptions import BadRequestKeyError

from database.crud.user_crud import User

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))

from database.crud.profile_crud import Profile
from database.crud.interactions_crud import Interactions
from utils.security import auth_guard
from utils.manage_interactions import ManageInteractions
from src.interactions import interactions_bp



@interactions_bp.route("/block", methods=["POST"])
@auth_guard
def block_user():
    '''Endpoint to block a user.
    Expects JSON body with key 'blocked_user' containing the username of the user to block.
    '''
    try:
        requested_data = request.json
        if "blocked_user" not in requested_data:
            return jsonify({"error": "Key error: request must include 'blocked_user' with the blocked user's username"}), 400
        
        connection_pool = current_app.config["CONNECTION_POOL"]
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
            return jsonify({"error": "blocked user does not exist"}), 409
        
        interactions_crud = Interactions(connection_pool, g.user_id, blocked_user_data["id"])
        interactions_crud.block_user()
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": e}), 409