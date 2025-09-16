import os
import sys
import logging

from flask import Blueprint, request, jsonify, current_app, g, send_file, url_for
from werkzeug.exceptions import BadRequestKeyError

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))

from database.crud.user_crud import User
from database.crud.profile_crud import Profile
from utils.validate_profile_data import validate_profile_data
from utils.security import auth_guard
from utils.fame_rating import calculate_fame_rating
from utils.image_handler import upload_pictures
from src.user_profile import profile_bp

logger = logging.getLogger(__name__)


@profile_bp.route("/set_location", methods=["POST"])
@auth_guard
def set_location():
    '''Set or update the geographical location for the logged-in user.
    Expects a JSON payload with the following fields:
    - latitude (float): Required. Latitude of the user's location.
    - longitude (float): Required. Longitude of the user's location.
    - city (string): Optional. City name.
    - country (string): Optional. Country name.
    - accuracy (int): Optional. Accuracy of the location in meters. Defaults to 50 if not provided.
    '''
    try:
        request_data = request.get_json()
        logger.debug(f"⚠️⚠️⚠️🔍 request data -> {request_data} ⚠️⚠️⚠️")

        required_fields = ['latitude', 'longitude']
        for field in required_fields:
            if field not in request_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        optional_fields = ['city', 'country', 'accuracy']
        for field in optional_fields:
            if field not in request_data:
                request_data[field] = None

        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        from database.crud.location_crud import Location
        location_crud = Location(connection_pool)
        
        location_crud.set_user_location(
            user_id=g.user_id,
            latitude=request_data['latitude'],
            longitude=request_data['longitude'],
            city=request_data['city'],
            country=request_data['country'],
            accuracy=request_data['accuracy'] if request_data['accuracy'] is not None else 50
        )

        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logger.error(f"Error setting location: {e}")
        return jsonify({"error": "Internal server error"}), 500