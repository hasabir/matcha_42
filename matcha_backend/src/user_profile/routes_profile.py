from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app, g, send_file, url_for
from database.crud.interactions_crud import Interactions
from database.crud.location_crud import Location
from database.crud.user_crud import User
from database.crud.matching_operations_crud import Matching
from src.user_profile import profile_bp
from utils.ip_geolocation import get_location_from_ip, get_client_ip, reverse_geocode
import sys
import os

from utils.profile_utils import get_profile_data, houres_between_dates, format_last_seen
from utils.validate_profile_data import validate_profile_data
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
import logging
from utils.security import auth_guard
from utils.fame_rating import calculate_fame_rating
from utils.notification_service import NotificationService
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
        # Support both JSON and multipart/form-data bodies
        if request.content_type and 'application/json' in request.content_type:
            request_data = (request.get_json(silent=True) or {})
        else:
            request_data = request.form.to_dict()

        request_data["user_id"] = g.user_id
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        profile_crud = Profile(connection_pool)
        profile = profile_crud.get_profile_by_user_id(request_data["user_id"])
        if profile:
            return jsonify({"error": "profile already created"}), 409

        # Validate fields; function raises ValueError on failure
        try:
            validate_profile_data(request_data)
        except ValueError as ve:
            return jsonify({
                "error": "Validation failed",
                "details": str(ve)
            }), 400

        # Only try to read files if it's a multipart/form-data request
        requested_file = None
        if request.content_type and 'multipart/form-data' in request.content_type:
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
    
    # Fields that belong to the users table (not profiles table)
    user_fields = ["first_name", "last_name", "email"]
    user_data = {}
    for item in user_fields:
        if item in request_data:
            user_data[item] = request_data[item]
            del request_data[item]
    
    # Validate email uniqueness if email is being updated
    if "email" in user_data:
        existing_user = user_crud.get_user_by_email(user_data["email"])
        if existing_user and existing_user.get("id") != g.user_id:
            return jsonify({"error": "Email already in use by another account"}), 409
    
    logger.debug(f"👉👉👉👉 user_data {user_data}")
    logger.debug(f"👉👉👉👉 request_data {request_data}")
    
    if request_data:
        profile_crud.update_profile(g.user_id, request_data)
    if user_data:
        user_crud.update_user(user_data, username=None, user_id=g.user_id)
    return jsonify({"status": "ok"}), 201




@profile_bp.route("/get_user_by_id/<int:user_id>")
@auth_guard
def get_user_by_id(user_id):
    '''Get basic user information by user_id (returns username mainly, for notifications)'''
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        
        user_crud = User(connection_pool)
        user_data = user_crud.get_user_by_id(user_id)
        
        if not user_data:
            return jsonify({"error": "User not found"}), 404
        
        # Return only safe, basic information
        return jsonify({
            "username": user_data.get("username"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name")
        }), 200
        
    except Exception as e:
        logger.exception("Error getting user by ID")
        return jsonify({"error": str(e)}), 500


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
        if username == "me" \
            or user_crud.get_user_by('id', g.user_id, 'username')["username"] == username:
            
            # Include sensitive data (email) for own profile
            profile_data = get_profile_data(connection_pool, g.user_id, include_sensitive=True)
            return jsonify({"result": profile_data}), 200

        user_data = user_crud.get_user_by_username(username=username)
        if not user_data:
            return jsonify({"error": "user not found"}), 404

        interactions_crud = Interactions(connection_pool, g.user_id, user_data["id"])
            
        # Check if blocked in either direction
        if interactions_crud.is_blocked():
            return jsonify({"error": "You are blocked by this user"}), 403
        if interactions_crud.did_i_block():
            return jsonify({"error": "You have blocked this user"}), 403
        notification_service = NotificationService(connection_pool)
        
        notification_service.create_notification(
                user_id=user_data["id"],
                notification_type="profile_view",
                reference_id=g.user_id,
            )
        
        # Get profile data WITHOUT sensitive information for other users
        profile_data = get_profile_data(connection_pool, user_data["id"], include_sensitive=False)
        
        # Add interaction status information
        matching_crud = Matching(connection_pool)
        
        # Get the user's online status from the database (active field)
        user_status = user_crud.get_user_status(user_data["id"])
        is_online = user_status.get('active', False) if user_status else False
        
        # Build interaction status object
        profile_data["interaction_status"] = {
            "i_liked_them": interactions_crud.did_i_like(),
            "they_liked_me": interactions_crud.is_liked_by(),
            "we_are_connected": matching_crud.are_matched(g.user_id, user_data["id"]),
            "i_blocked_them": interactions_crud.did_i_block(),
            "they_blocked_me": interactions_crud.is_blocked(),
            "i_reported_them": interactions_crud.has_reported(),
            "is_online": is_online,
            "last_seen_formatted": format_last_seen(profile_data.get('last_seen'))
        }
        
        #set profile visit and increment profile views count
        last_visit = profile_crud.check_last_visit(g.user_id, user_data["id"])
        hours_passed = houres_between_dates(last_visit) if last_visit else None
        
        if hours_passed is None:
            # First visit - increment profile views
            profile_crud.set_user_visited(g.user_id, user_data["id"])
            profile_crud.increment_profile_views(user_data["id"])
            new_rating = calculate_fame_rating(profile_data.get('fame_rating', 0), type='visit')
            profile_crud.update_fame_rating(user_data["id"], new_rating)
        elif hours_passed >= 24:
            # Visit after 24 hours - increment profile views again
            profile_crud.set_user_visited(g.user_id, user_data["id"])
            profile_crud.increment_profile_views(user_data["id"])
            new_rating = calculate_fame_rating(profile_data.get('fame_rating', 0), type='visit')
            profile_crud.update_profile_vist_timestamp(g.user_id, user_data["id"])
            profile_crud.update_fame_rating(user_data["id"], new_rating)
    
        return jsonify({"result": profile_data, "houres_passed": hours_passed}), 200
    except Exception as e:
        logger.exception("Error in get_profile")
        return jsonify({"error": str(e)}), 409
    
    
@profile_bp.route("/get_profile_visitors", methods=["GET"])
@auth_guard
def get_profile_visitors():
    '''get the profile visitors of the logged in user'''
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        
        profile_crud = Profile(connection_pool)
        logger.info(f"Fetching profile visitors for user_id: {g.user_id}")
        
        result = profile_crud.get_profile_views(g.user_id)
        logger.info(f"Found {len(result)} visitors")
        
        user_crud = User(connection_pool)
        for view in result:
            try:
                user_info = user_crud.get_user_by('id', view["visitor_id"], '*')
                if user_info and 'id' in user_info:
                    view["username"] = user_info.get("username")
                    view["first_name"] = user_info.get("first_name", "")
                    view["last_name"] = user_info.get("last_name", "")
                else:
                    logger.warning(f"Could not find user info for visitor_id: {view['visitor_id']}")
            except Exception as user_e:
                logger.error(f"Error fetching user info for visitor_id {view.get('visitor_id')}: {user_e}")
                # Continue processing other visitors even if one fails
                continue
        
        return jsonify({'result': result}), 200
    except Exception as e:
        logger.exception("Error getting profile visitors")
        return jsonify({"error": str(e)}), 500

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
        logger.error(f"Error getting fame rating: {str(e)}")
        return jsonify({"error": str(e)}), 409


@profile_bp.route("/my_profile", methods=["GET"])
@auth_guard
def my_profile():
    '''Get basic profile info for the logged in user to check if profile exists'''
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        
        user_crud = User(connection_pool)
        profile_crud = Profile(connection_pool)
        
        # Get user data using get_user_by method
        user_data = user_crud.get_user_by('id', g.user_id, '*')
        if not user_data or 'id' not in user_data:
            return jsonify({"error": "User not found"}), 404
        
        # Check if profile exists
        profile = profile_crud.get_profile_by_user_id(g.user_id)
        has_profile = profile is not None
        
        return jsonify({
            "user_id": g.user_id,
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "has_profile": has_profile,
            "profile": profile if has_profile else None
        }), 200
        
    except Exception as e:
        logger.exception("Error fetching my_profile")
        return jsonify({"error": str(e)}), 500


@profile_bp.route("/user_status/<username>", methods=["GET"])
@auth_guard
def get_user_status(username):
    """Get online status and last_seen for a user"""
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        
        user_crud = User(connection_pool)
        
        # Get user by username
        user_data = user_crud.get_user_by_username(username)
        if not user_data:
            return jsonify({"error": f"User '{username}' not found"}), 404
        
        # Get status
        status = user_crud.get_user_status(user_data['id'])
        if not status:
            return jsonify({"error": "Failed to get user status"}), 500
        
        # Format response
        response_data = {
            "user_id": status['id'],
            "username": status['username'],
            "is_online": status.get('active', False),
            "last_seen": status['last_seen'].isoformat() if status.get('last_seen') else None
        }
        
        return jsonify({"result": response_data}), 200
        
    except Exception as e:
        logger.exception(f"Error fetching user status for {username}")
        return jsonify({"error": str(e)}), 500


@profile_bp.route("/get_profile_likes", methods=["GET"])
@auth_guard
def get_profile_likes():
    """Get likes for the current user's profile"""
    try:
        connection_pool = current_app.config.get("CONNECTION_POOL")
        
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        
        profile_crud = Profile(connection_pool)
        
        # Get users who liked this profile
        likes = profile_crud.get_profile_likes(g.user_id)
        
        return jsonify({
            "status": "ok",
            "likes": likes,
            "count": len(likes) if likes else 0
        }), 200
        
    except Exception as e:
        logger.exception("Error getting profile likes")
        return jsonify({"error": str(e)}), 500


@profile_bp.route("/detect_location", methods=["POST"])
@auth_guard
def detect_location():
    """
    Detect user location using GPS coordinates (from request) or IP fallback
    Expects JSON body with optional 'latitude' and 'longitude' fields
    If GPS coordinates not provided, falls back to IP geolocation
    """
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        
        data = request.get_json() or {}
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        location_crud = Location(connection_pool)
        
        # If GPS coordinates provided, use them
        if latitude is not None and longitude is not None:
            # Validate coordinates
            try:
                lat = float(latitude)
                lon = float(longitude)
                
                logger.info(f"Validating GPS coordinates for user {g.user_id}: lat={lat}, lon={lon}")
                
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    logger.warning(f"GPS coordinates out of range: lat={lat}, lon={lon}")
                    return jsonify({"error": "Coordinates out of valid range"}), 400
                
                # Perform reverse geocoding if city/country not provided
                city = data.get('city')
                country = data.get('country')
                
                if not city or not country:
                    logger.info(f"🌍 Performing reverse geocoding for ({lat}, {lon})...")
                    geocode_result = reverse_geocode(lat, lon)
                    if geocode_result:
                        city = city or geocode_result.get('city')
                        country = country or geocode_result.get('country')
                        logger.info(f"✅ Reverse geocoding successful: {city}, {country}")
                    else:
                        logger.warning(f"⚠️ Reverse geocoding failed for ({lat}, {lon})")
                
                # Update or create location
                location_data = {
                    'user_id': g.user_id,
                    'latitude': lat,
                    'longitude': lon,
                    'accuracy': data.get('accuracy'),
                    'city': city,
                    'country': country
                }
                
                # Check if location exists and update/create
                try:
                    existing_location = location_crud.get_location_by_user_id(g.user_id)
                    if existing_location:
                        location_crud.update_location(g.user_id, location_data)
                        logger.info(f"✅ Updated GPS location for user {g.user_id}: {lat}, {lon}")
                    else:
                        location_crud.create_location(location_data)
                        logger.info(f"✅ Created GPS location for user {g.user_id}: {lat}, {lon}")
                except Exception as db_error:
                    logger.exception(f"❌ Database error while saving location for user {g.user_id}")
                    return jsonify({
                        "error": "Database error while saving location",
                        "message": "Unable to save your location. Please try again later."
                    }), 500
                
                return jsonify({
                    "status": "success",
                    "message": "Location updated from GPS",
                    "location": {
                        "latitude": lat,
                        "longitude": lon,
                        "city": city,
                        "country": country,
                        "source": "gps"
                    }
                }), 200
                
            except (ValueError, TypeError) as e:
                logger.error(f"❌ Invalid coordinate format for user {g.user_id}: {latitude}, {longitude} - Error: {str(e)}")
                return jsonify({"error": f"Invalid coordinate format: {str(e)}"}), 400
        
        # Fallback to IP geolocation
        client_ip = get_client_ip(request)
        logger.info(f"Attempting IP geolocation for user {g.user_id}, IP: {client_ip}")
        
        ip_location = get_location_from_ip(client_ip)
        
        if ip_location:
            # Update or create location
            location_data = {
                'user_id': g.user_id,
                'latitude': ip_location['latitude'],
                'longitude': ip_location['longitude'],
                'city': ip_location.get('city'),
                'country': ip_location.get('country')
            }
            
            # Check if location exists and update/create
            try:
                existing_location = location_crud.get_location_by_user_id(g.user_id)
                if existing_location:
                    location_crud.update_location(g.user_id, location_data)
                    logger.info(f"✅ Updated IP-based location for user {g.user_id}: {ip_location.get('city')}, {ip_location.get('country')}")
                else:
                    location_crud.create_location(location_data)
                    logger.info(f"✅ Created IP-based location for user {g.user_id}: {ip_location.get('city')}, {ip_location.get('country')}")
            except Exception as db_error:
                logger.exception(f"❌ Database error while saving IP-based location for user {g.user_id}")
                return jsonify({
                    "error": "Database error while saving location",
                    "message": "Unable to save your location. Please try again later."
                }), 500
            
            return jsonify({
                "status": "success",
                "message": "Location detected from IP address",
                "location": ip_location
            }), 200
        else:
            # Location detection failed (common in development with localhost)
            # Return success but indicate location is not available
            logger.warning(f"⚠️ Could not detect location for user {g.user_id} (IP: {client_ip})")
            return jsonify({
                "status": "warning",
                "message": "Location could not be detected automatically. This is normal in development environments.",
                "location": None
            }), 200
        
    except Exception as e:
        logger.exception("Error detecting location")
        return jsonify({"error": str(e)}), 500