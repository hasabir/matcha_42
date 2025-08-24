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


def get_tags(request_data):
    if not request_data or "tags" not in request_data:
        return "error: missing required field : <tags>"
    if not isinstance(request_data["tags"], list):
        return "error: tags must be in a list"
    parsed_tags = []
    for tag in request_data["tags"]:
        parsed_tags.append(tag.strip("#").lower())
    return parsed_tags
    # if request_data[""]

@profile_bp.route("/add_tags", methods=["POST"])
@auth_guard
def add_tags():
    request_data = request.json
    connection_pool = current_app.config["CONNECTION_POOL"]
    profile_crud = Profile(connection_pool)
    if not  connection_pool:
        return jsonify({"error": "Database connection pool is not available"}), 500
    #TODO -> pars tags
    tags = get_tags(request_data)
    for tag in tags:
        tag_result = profile_crud.insert_tag(tag)
        profile_crud.add_user_interests(g.user_id, tag_result["tag_id"])
    return jsonify({"status": "ok"}), 200