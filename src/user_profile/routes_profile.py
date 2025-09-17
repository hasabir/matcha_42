from flask import Blueprint, request, jsonify, current_app, g, send_file, url_for
from database.crud.user_crud import User
from src.user_profile import profile_bp
import sys
import os

from utils.validate_profile_data import validate_profile_data
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
import logging
from utils.security import auth_guard
from utils.fame_rating import calculate_fame_rating
from  database.crud.profile_crud import Profile
from utils.image_handler import upload_pictures
from werkzeug.exceptions import BadRequestKeyError
# profile_bp = Blueprint('user_profile', __name__)
logger = logging.getLogger(__name__)

@profile_bp.route("/create_profile", methods=["POST"])
@auth_guard
def create_profile():
    '''create a profile for the logged in user
    Expects a multipart/form-data request with profile fields and an optional 'profile_pic' file.
    Example fields: bio, age, sexual_preferences, gender
    '''
    try:
        request_data = request.form.to_dict()

        request_data["user_id"] = g.user_id
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        profile_crud = Profile(connection_pool)
        profile = profile_crud.get_profile_by_user_id(request_data["user_id"])
        if profile:
            return jsonify({"error": "profile already created"}), 409

        validation_errors = validate_profile_data(request_data)
        if validation_errors:
            return jsonify({
                "error": "Validation failed",
                "details": validation_errors
            }), 400

        requested_file = request.files.get('profile_pic', None)
        profile_path = upload_pictures(requested_file, g.user_id) if requested_file else None
        url_path = url_for('static', filename=profile_path) if requested_file else None
        request_data["profile_picture"] = url_path if requested_file else None
        request_data["fame_rating"] = calculate_fame_rating()

        profile_crud.create_profile(request_data)
        return jsonify({"status": "ok"}), 201

    except BadRequestKeyError:
        return jsonify({"error": "KeyError, file must be stored with key = profile_pic"}), 415
    except Exception as e:
        logger.exception("Error creating profile")
        return jsonify({"error": str(e)}), 409



@profile_bp.route("/update_profile", methods=['POST'])
@auth_guard
def update_profile():
    '''update the profile for the logged in user
    Expects a json body with profile fields to update.'''

    request_data = request.json
    connection_pool = current_app.config["CONNECTION_POOL"]
    if not connection_pool:
        return jsonify({"error": "Database connection pool is not available"}), 500
    profile_crud = Profile(connection_pool)
    user_crud = User(connection_pool)
    
    user_fields = ["first_name", "last_name"] #! location?
    user_data = {}
    for item in user_fields:
        if item in request_data:
            user_data[item] = request_data[item]
            del request_data[item]
    logger.debug(f"👉👉👉👉 request_data {user_data}")
    logger.debug(f"👉👉👉👉 request_data {request_data}")
    
    if user_data:
        profile_crud.update_profile(g.user_id, request_data)
    if request_data:
        user_crud.update_user(user_data, username=None, user_id=g.user_id)
    return jsonify({"status": "ok"}), 201





@profile_bp.route("/search_profile/<username>")
@auth_guard
def get_profile(username):
    '''get the profile of a user by username '''
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not  connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        profile_crud = Profile(connection_pool)
        user_crud = User(connection_pool)
        user_data = user_crud.get_user_by_username(username=username)
        if not user_data:
            return jsonify({"error": "user not found"}), 404

        #TODO check first if the user is not blocked then continue
        #TODO return intersts and images also

        profile_data = profile_crud.get_profile_by_user_id(user_data["id"])
        profile_data["tags"] = profile_crud.get_user_interests(user_data["id"])
        return jsonify({"result": profile_data}), 200
    except Exception as e:
        return jsonify({"error": "requied field <tag>"}), 409

