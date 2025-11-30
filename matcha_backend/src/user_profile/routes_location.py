import os
import sys
import logging

from flask import Blueprint, request, jsonify, current_app, g, send_file, url_for
from werkzeug.exceptions import BadRequestKeyError

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))

from database.crud.interactions_crud import Interactions
from database.crud.user_crud import User
from database.crud.profile_crud import Profile
from utils.validate_profile_data import validate_profile_data
from utils.security import auth_guard
from utils.fame_rating import calculate_fame_rating
from utils.image_handler import upload_pictures
from src.user_profile import profile_bp

logger = logging.getLogger(__name__)


@profile_bp.route("/set_location", methods=["POST", "PUT"])
@auth_guard
def set_location():
    '''Set or update the geographical location for the logged-in user.
    Expects a JSON payload with the following fields:
    - latitude (float): Required. Latitude of the user's location.
    - longitude (float): Required. Longitude of the user's location.
    - city (string): Optional. City name.
    - country (string): Optional. Country name.
    - neighborhood (string): Optional. Neighborhood name (for neighborhood-level GPS positioning).
    - accuracy (int): Optional. Accuracy of the location in meters. Defaults to 50 if not provided.
    '''
    try:
        request_data = request.json
        logger.debug(f"⚠️⚠️⚠️🔍 request data -> {request_data} ⚠️⚠️⚠️")

        required_fields = ['latitude', 'longitude']
        for field in required_fields:
            if field not in request_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        optional_fields = ['city', 'country', 'neighborhood', 'accuracy']
        for field in optional_fields:
            if field not in request_data:
                request_data[field] = None

        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        from database.crud.location_crud import Location
        from utils.ip_geolocation import normalize_country_name
        location_crud = Location(connection_pool)
        
        # Normalize country name to ensure consistency
        if request_data.get('country'):
            request_data['country'] = normalize_country_name(request_data['country'])
        
        # If neighborhood is not provided by frontend, try to get it from coordinates
        if not request_data.get('neighborhood'):
            try:
                from utils.ip_geolocation import get_neighborhood_from_coords
                neighborhood = get_neighborhood_from_coords(
                    request_data['latitude'], 
                    request_data['longitude']
                )
                request_data['neighborhood'] = neighborhood
                if neighborhood:
                    logger.info(f"✅ Auto-detected neighborhood for user {g.user_id}: {neighborhood}")
            except Exception as e:
                logger.warning(f"⚠️ Could not auto-detect neighborhood: {e}")
        
        try:
            location_crud.set_user_location(
                user_id=g.user_id,
                latitude=request_data['latitude'],
                longitude=request_data['longitude'],
                city=request_data['city'],
                country=request_data['country'],
                neighborhood=request_data['neighborhood'],  # Neighborhood-level GPS positioning
                accuracy=request_data['accuracy'] if request_data['accuracy'] is not None else 50
            )
            logger.info(f"✅ Location set for user {g.user_id}: lat={request_data['latitude']}, lon={request_data['longitude']}, neighborhood={request_data.get('neighborhood', 'N/A')}")
        except Exception as db_error:
            logger.exception(f"❌ Database error while setting location for user {g.user_id}")
            return jsonify({
                "error": "Database error while saving location",
                "message": "Unable to save your location. Please try again later."
            }), 500

        return jsonify({"status": "ok"}), 200
        
    except BadRequestKeyError as e:
        logger.error(f"❌ Missing required field: {e}")
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except (ValueError, TypeError) as e:
        logger.error(f"❌ Invalid data format for user {g.user_id}: {str(e)}")
        return jsonify({"error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        logger.exception(f"❌ Unexpected error in set_location for user {g.user_id}")
        return jsonify({"error": "Internal server error"}), 500
    
    

@profile_bp.route("/nearby_users", methods=["GET"])
@auth_guard
def get_nearby_users():
    '''Retrieve a list of users located within a specified distance from the logged-in user.
    Query Parameters:
    - max_distance (float): Optional. Maximum distance in kilometers to search for nearby users. Defaults to 100km if not provided.
    '''
    try:
        user_id = g.user_id
        max_distance = request.args.get('max_distance', 100, type=float)  # Default 100km
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        from database.crud.location_crud import Location
        location_crud = Location(connection_pool)
        
        nearby_users = location_crud.find_nearby_users(user_id, max_distance)
        
        return jsonify({
            "status": "ok",
            "nearby_users": nearby_users,
            "count": len(nearby_users)
        }), 200
        
    except Exception as e:
        logger.error(f"Error finding nearby users: {e}")
        return jsonify({"error": "Internal server error"}), 500




@profile_bp.route("/get_location/<username>", methods=["GET"]) #?
@auth_guard
def get_user_location(username):
    '''Retrieve the geographical location of a specified user by username.
    If username is "me", retrieve the location of the logged-in user.
    '''
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        from database.crud.location_crud import Location
        location_crud = Location(connection_pool)

        user_crud = User(connection_pool)
        if username == "me"\
            or user_crud.get_user_by('id', g.user_id, 'username')["username"] == username:
            user_id = g.user_id
        else:
            user_data = user_crud.get_user_by_username(username=username)
            if not user_data:
                return jsonify({"error": "User not found"}), 404
            user_id = user_data["id"]
            interactions_crud = Interactions(connection_pool, g.user_id, user_id)
            # Check if blocked in either direction
            if interactions_crud.is_blocked():
                return jsonify({"error": "You are blocked by this user"}), 403
            if interactions_crud.did_i_block():
                return jsonify({"error": "You have blocked this user"}), 403

        location_data = location_crud.get_user_location(user_id)
        if not location_data:
            return jsonify({"error": "Location data not found for the user"}), 404

        return jsonify({
            "status": "ok",
            "location": location_data
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving user location: {e}")
        return jsonify({"error": "Internal server error"}), 500