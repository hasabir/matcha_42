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
    '''add interest tags for the logged in user
    Expects a json body with a "tags" field containing a list of tags.
    Example: { "tags": ["music", "sports", "travel"] }'''
    try:
        request_data = request.json
        connection_pool = current_app.config["CONNECTION_POOL"]
        profile_crud = Profile(connection_pool)
        if not  connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        tags = get_tags(request_data)
        for tag in tags:
            tag_result = profile_crud.insert_tag(tag)
            profile_crud.add_user_interests(g.user_id, tag_result["tag_id"])
        return jsonify({"status": "ok"}), 201
    except Exception as e:
        return jsonify({"error": e}), 409


@profile_bp.route("/delete_tag", methods=["POST"])
@auth_guard
def delet_tag():
    '''remove an interest tag for the logged in user    
    Expects a json body with a "tag" field containing a single tag.
    Example: { "tag": "music" }'''
    try:
        request_data = request.json
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not  connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        profile_crud = Profile(connection_pool)
        if not isinstance(request_data["tag"], str):
            return jsonify({"error": "tag must be a string"}), 415
        tag_id = profile_crud.get_tag_id(request_data["tag"])
        if not tag_id:
            return jsonify({"error": "user does not have request interst"}), 401
        user_id  = g.user_id
        profile_crud.remove_user_interest(user_id=user_id, tag_id=tag_id["tag_id"])
        return jsonify({"status": "ok"}), 201
    except KeyError:
        return jsonify({"error": "requied field <tag>"}), 415
    except Exception as e:
        return jsonify({"error": e}), 409

    
@profile_bp.route("/get_user_tags") #! do I really need this endpoint 🤪
@auth_guard
def get_user_interests():
    '''get interest tags for the logged in user'''
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not  connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        profile_crud = Profile(connection_pool)
        result = profile_crud.get_user_interests(g.user_id)
        return jsonify({'result': result}), 200
    except Exception as e:
        return jsonify({"error": e}), 409
