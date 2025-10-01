from flask import Blueprint, request, jsonify, current_app, g
from database.crud.search_crud import Search
from database.crud.user_crud import User
from src.search import search_bp
import sys
import os

from utils import validate_sort_data
from utils.validate_search_data import validate_search_data
from utils.validate_profile_data import validate_profile_data
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
import logging
from utils.security import auth_guard
from  database.crud.profile_crud import Profile



logger = logging.getLogger(__name__)


@search_bp.route("/sort", methods=["POST"])
@auth_guard
def sort_users():
    '''sort users based on criteria
    Expects a json body with sort criteria and list of usernames.
    Example: { "sort_by": "age" or "fame_rating" or "location" or "interests",
    "order": "asc" or "desc",
    "usernames": [user1, user2, user3] }'''
    try:
        request_data = request.json
        if not request_data:
            return jsonify({"error": "Invalid JSON data"}), 400

        valide_request = validate_sort_data(request_data)
        if not valide_request[0]:
            return jsonify({"error": valide_request[1]}), 400
        
        
        cnnection_pool = current_app.config["CONNECTION_POOL"]
        if not  cnnection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        search_curd = Search(cnnection_pool)
        profiles = search_curd.sort_users(request_data["usernames"], request_data["sort_by"],\
            request_data["order"], g.user_id, request_data.get("max_distance_km", 100) if request_data["sort_by"] == "location" else None)
        
        
        return jsonify({"profiles": profiles}), 200

    except Exception as e:
        logger.error(f"Error in /sort endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500