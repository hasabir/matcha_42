from flask import Blueprint, request, jsonify, current_app, g
from database.crud.search_crud import Search
from database.crud.user_crud import User
from src.search import search_bp
import sys
import os

from utils.validate_search_data import validate_search_data
from utils.validate_profile_data import validate_profile_data
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
import logging
from utils.security import auth_guard
from  database.crud.profile_crud import Profile



logger = logging.getLogger(__name__)


@search_bp.route("/filter", methods=["POST"])
@auth_guard
def filter():
    '''Filter users based on criteria
    Expects a json body with 
    usernames list and at least one other
    criteria dictionnary that containes filter criteria.
    Example: { "age_range": {"min_age": 20, 'max_age: 30},
    "location": {"city":"Ben Guerir", "country": "Morocco"} or "coordinates": {"latitude": 32.2958, "lngitude": -6.9278}, "distance": 10,},
    "interests": ["music", "sports"] }'''
    # try:
    request_data = request.json
    if not request_data or len(request_data) != 2 or any(key not in request_data for key in ['usernames', 'createria']):
        return jsonify({"error": "At least two fields are required, including 'usernames' and 'createria'."}), 400
        
    if 'usernames' in request_data:
        usernames = request_data['usernames']
        if not isinstance(usernames, list) or not all(isinstance(username, str) for username in usernames):
            return False, "Invalid usernames. It should be a list of strings."
    else:
        return jsonify({"error": "'usernames' field is required."}), 400
    

    check_request = validate_search_data(request_data['createria'])
    if not check_request[0]:
        return jsonify({"error": check_request[1]}), 400
    
    connection_pool = current_app.config["CONNECTION_POOL"]
    
    if not  connection_pool:
        return jsonify({"error": "Database connection pool is not available"}), 500
    # Extract search criteria from request_data
    
    search_crud = Search(connection_pool, filter=True)
    results = search_crud.filter_users(request_data["usernames"], request_data['createria'])
    return jsonify({"results": results}), 200
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500