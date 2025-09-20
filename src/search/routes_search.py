from flask import Blueprint, request, jsonify, current_app, g
from database.crud.user_crud import User
from src.search import search_bp
import sys
import os

from utils.validate_profile_data import validate_profile_data
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
import logging
from utils.security import auth_guard
from  database.crud.profile_crud import Profile






logger = logging.getLogger(__name__)


@search_bp.route("/search_users", methods=["POST"])
@auth_guard
def search_users():
    '''search for users based on criteria
    Expects a json body with search criteria.
    Example: { "age_range": {"min_age": 20, 'max_age: 30},
    "location": {"city":"Ben Guerir", "country": "Morocco"} or "coordinates": {"latitude": 32.2958, "lngitude": -6.9278}, "distance": 10,},
    "interests": ["music", "sports"] }'''
    try:
        request_data = request.json
        check_request = validate_profile_data(request_data)
        if not check_request[0]:
            return jsonify({"error": check_request[1]}), 400
        
        connection_pool = current_app.config["CONNECTION_POOL"]
        profile_crud = Profile(connection_pool)
        if not  connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        # Extract search criteria from request_data
        results = 'test' 
        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500