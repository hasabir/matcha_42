from flask import Blueprint, request, jsonify, current_app, g
from database.crud.user_crud import User
from src.user_profile import profile_bp
import sys
import os

from utils.validate_profile_data import validate_profile_data
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
import logging
from utils.security import auth_guard
from  database.crud.profile_crud import Profile



logger = logging.getLogger(__name__)



@profile_bp.route("/add_tags", methods=["POST"])
@auth_guard
def add_tags():
    request_data = request.json
    connection_pool = current_app.config["CONNECTION_POOL"]
    profile_crud = Profile(connection_pool)
    if not  connection_pool:
        return jsonify({"error": "Database connection pool is not available"}), 500
    #TODO -> pars tags
    tag_result = profile_crud.insert_tag(request_data["tags"])
    # tag_id = tag_result[0]['tag_id']
    logger.debug(f"👉 👉 👉 👉 👉 👉 {tag_result}")
    # profile_crud.add_user_interests(g.user_id, tag_id)
    return jsonify({"status": "ok"}), 200