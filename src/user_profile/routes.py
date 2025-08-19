from flask import Blueprint, request, jsonify, current_app
from src.user_profile import profile_bp
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
import logging

from  database.crud.profile_crud import Profile

# profile_bp = Blueprint('user_profile', __name__)

@profile_bp.route('/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    # Logic to retrieve user profile by user_id
    return jsonify({"message": f"Profile for user {user_id}"}), 200

@profile_bp.route('/getprofiles', methods=['GET'])
def get_all_profiles():
    logging.info("*********************Fetching all profiles**********")
    connection_pool = current_app.config["CONNECTION_POOL"]
    if not connection_pool:
        return jsonify({"error": "Database connection pool is not available"}), 500
    profile = Profile(connection_pool)
    result = profile.get_all_profiles()
    return jsonify({"status": "ok", "data": result}), 200