import os
import sys
import logging

from flask import Blueprint, flash, request, jsonify, current_app, g, send_file, url_for
from werkzeug.exceptions import BadRequestKeyError

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))

from database.crud.matching_operations_crud import Matching
from database.crud.user_crud import User
from database.crud.profile_crud import Profile
from database.crud.interactions_crud import Interactions
from utils.validate_profile_data import validate_profile_data
from utils.security import auth_guard
from utils.fame_rating import calculate_fame_rating
from utils.manage_interactions import ManageInteractions
from utils.image_handler import upload_pictures
from src.interactions import interactions_bp
from utils.matching_algo import matching_suggestions



logger = logging.getLogger(__name__)


@interactions_bp.route("/get_matching_suggestions", methods=["GET"])
@auth_guard
def get_matching_suggestions():
    '''Get matched users for the authenticated user.'''
    # try:
    connection_pool = current_app.config["CONNECTION_POOL"]
    if not  connection_pool:
        return jsonify({"error": "Database connection pool is not available"}), 500
    # matching_curd = Matching(connection_pool)
    # matched_users = matching_curd.get_matched_users(g.user_id)#?
    matching_suggestions_list = matching_suggestions(connection_pool, g.user_id)
    # matched_users = []  # Placeholder for matched users list
    
    return jsonify({"matching suggestions list": matching_suggestions_list}), 200

