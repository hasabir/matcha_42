from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app, g, send_file, url_for
from database.crud.interactions_crud import Interactions
from database.crud.location_crud import Location
from database.crud.user_crud import User
from src.user_profile import profile_bp
import sys
import os

from utils.profile_utils import get_profile_data, houres_between_dates
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
        request_data["fame_rating"] = calculate_fame_rating(type='create_profile')

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
    
    user_fields = ["first_name", "last_name"]
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





@profile_bp.route("/get_profile/<username>")
@auth_guard
def get_profile(username):
    '''get the profile of a user by username if username is "me" get the profile of the logged in user'''
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not  connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        profile_crud = Profile(connection_pool)
        
        user_crud = User(connection_pool)
        
        # if the username is "me" or the logged in user's username get the logged in user's profile
        test = user_crud.get_user_by('id', g.user_id, 'username')
        if username == "me" \
            or user_crud.get_user_by('id', g.user_id, 'username')["username"] == username:
            
            profile_data = get_profile_data(connection_pool, g.user_id)
            return jsonify({"result": profile_data}, test), 200

        user_data = user_crud.get_user_by_username(username=username)
        if not user_data:
            return jsonify({"error": "user not found"}), 404

        interactions_crud = Interactions(connection_pool, g.user_id, user_data["id"])
            
        if interactions_crud.is_blocked():
            return jsonify({"error": "You are blocked by this user"}), 403
        
        profile_data = get_profile_data(connection_pool, user_data["id"])
        
        #set profile visit
        #TODO notify other user of visit
        last_visit = profile_crud.check_last_visit(g.user_id, user_data["id"])
        hours_passed = houres_between_dates(last_visit) if last_visit else None
        
        if hours_passed is None:
            profile_crud.set_user_visited(g.user_id, user_data["id"])
            new_rating = calculate_fame_rating(profile_data['fame_rating'], type='visit')
            profile_crud.update_fame_rating(user_data["id"], new_rating)
        elif hours_passed >= 24:
            profile_crud.set_user_visited(g.user_id, user_data["id"])
            new_rating = calculate_fame_rating(profile_data['fame_rating'], type='visit')
            profile_crud.update_profile_vist_timestamp(g.user_id, user_data["id"])
            profile_crud.update_fame_rating(user_data["id"], new_rating)
    
        return jsonify({"result": profile_data, "houres_passed": hours_passed}), 200
    except Exception as e:
        return jsonify({"error": e}), 409
    
    
@profile_bp.route("/get_profile_vistors", methods=["GET"])
@auth_guard
def get_profile_vistors():
    '''get the profile visitors of the logged in user'''
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not  connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        profile_crud = Profile(connection_pool)
        result = profile_crud.get_profile_views(g.user_id)
        user_crud = User(connection_pool)
        for view in result:
            user_info = user_crud.get_user_by_id(view["visitor_id"])
            view["username"] = user_info["username"]
        return jsonify({'result': result}), 200
    except Exception as e:
        return jsonify({"error": e}), 409

@profile_bp.route("/get_fame_rating", methods=["GET"])
@auth_guard
def fame_rating():
    '''get the fame rating of the logged in user'''
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not  connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        profile_crud = Profile(connection_pool)
        fame_rating = profile_crud.get_fame_rating(g.user_id)
        return jsonify({'fame_rating': fame_rating}), 200
    except Exception as e:
        return jsonify({"error": e}), 409