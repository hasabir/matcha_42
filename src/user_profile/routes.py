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

# profile_bp = Blueprint('user_profile', __name__)
logger = logging.getLogger(__name__)

@profile_bp.route("/create_profile", methods=["POST"])
@auth_guard
def create_profile():
    try:
        request_data = request.json
        request_data["user_id"] = g.user_id
        connection_pool = current_app.config["CONNECTION_POOL"]
        profile_crud = Profile(connection_pool)
        if not  connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        
        
        profile = profile_crud.get_profile_by_user_id(request_data["user_id"])
        if profile:
            return jsonify({"error": "profile already created"}), 401
        
        validation_errors = validate_profile_data(request_data)

        if validation_errors:
            return jsonify({
                "error": "Validation failed",
                "details": validation_errors
            }), 400
        
        if not all([request_data["bio"],
                    request_data["gender"], request_data["age"],
                    request_data['location'], request_data['profile_picture'],
                    request_data["fame_rating"], request_data["sexual_preferences"]]):
            return jsonify({"error": "Missing required fields:\
                <bio>, <gender>, <profile_picture>, \
                    <fame_rating>, <sexual_preferences>"}), 400

        profile_crud.create_profile(request_data)
        
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": e}), 409



@profile_bp.route("/update_profile", methods=['POST'])
@auth_guard
def update_profile():
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


@profile_bp.route('/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    # Logic to retrieve user profile by user_id
    return jsonify({"message": f"Profile for user {user_id}"}), 200

@profile_bp.route('/get_all_profiles', methods=['GET'])
def get_all_profiles():
    logging.info("*********************Fetching all profiles**********")
    connection_pool = current_app.config["CONNECTION_POOL"]
    if not connection_pool:
        return jsonify({"error": "Database connection pool is not available"}), 500
    profile = Profile(connection_pool)
    result = profile.get_all_profiles()
    return jsonify({"status": "ok", "data": result}), 200