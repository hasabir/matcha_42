import os
import sys
import logging

from flask import Blueprint, flash, request, jsonify, current_app, g, send_file, url_for
from werkzeug.exceptions import BadRequestKeyError

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))

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
    try:
        requested_data = request.json
        #TODO validate request data
        if "liked_user" not in requested_data:
            return jsonify({"error": "Key error: request must include 'liked_user' with the liked user's username"}), 400
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        profile_crud = Profile(connection_pool)
        profile = profile_crud.get_profile_by_user_id(g.user_id)
        if not profile["profile_picture"]:
            return jsonify({"error": "You need profile picture to complete this action"}), 409
        liked_user_crud = User(connection_pool)
        liked_user_data = liked_user_crud.get_user_by_username(username=requested_data["liked_user"])
        if not liked_user_data:
            return jsonify({"error": "liked user does not exist"}), 409
        interactions_crud = Interactions(connection_pool, g.user_id, liked_user_data["id"])
        manage_interactions = ManageInteractions(connection_pool, interactions_crud)
        if manage_interactions.check_action(g.user_id, liked_user_data["id"]) == "like":
            interactions_crud.like_user()
        else:
            interactions_crud.dislike_user()
        return jsonify({"status": "ok",
                        "message": f"likded user id = {liked_user_data}\
                        other username = {requested_data["liked_user"]}"}), 201
    except Exception as e:
        return jsonify({"error": e}), 400


