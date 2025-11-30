from flask import Blueprint, request, jsonify, current_app, g
from database.crud.search_crud import Search
from database.crud.user_crud import User
from database.crud.profile_crud import Profile
from database.crud.location_crud import Location
from database.crud.interactions_crud import Interactions
from src.search import search_bp
from utils.security import auth_guard
from utils.validate_search_data import validate_search_data
from utils.profile_utils import get_profile_data
from psycopg2.extras import RealDictCursor
import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
logger = logging.getLogger(__name__)


@search_bp.route("/users", methods=["POST"])
@auth_guard
def search_users():
    """
    ADVANCED search endpoint - searches users with ALL criteria at once.
    
    This endpoint allows searching with multiple criteria simultaneously:
    - Age range
    - Fame rating range  
    - Location (GPS coordinates or city/country)
    - Interest tags (with AND/OR matching)
    - Gender
    - Sorting
    
    Request Body (JSON):
    {
        "age_range": {
            "min_age": 18,      // optional
            "max_age": 99       // optional
        },
        "fame_rating": {
            "min": 0,           // optional
            "max": 100          // optional
        },
        "location": {
            "city": "Paris",    // optional - search by city name
            "country": "France" // optional - search by country name
        },
        "coordinates": {
            "latitude": 48.8566,   // optional - GPS coordinates for radius search
            "longitude": 2.3522,
            "distance": 50         // optional - radius in km (default: 100)
        },
        "interests": ["Music", "Travel"],  // optional - interest tags
        "interests_match_mode": "OR",      // optional - "AND" or "OR" (default: "OR")
        "gender": "female",     // optional - filter by gender
        "sort_by": "fame_rating",  // optional - age, fame_rating, distance, interests, city, country
        "sort_order": "desc"    // optional - asc or desc (default: desc)
    }
    
    Returns:
        JSON with list of matching user profiles with full details (filtered and sorted)
    """
    try:
        request_data = request.json if request.json else {}
        
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        
        search_crud = Search(connection_pool, filter=False)
        user_crud = User(connection_pool)
        profile_crud = Profile(connection_pool)
        location_crud = Location(connection_pool)
        
        logger.info(f"🔍 Advanced search requested by user_id: {g.user_id}")
        logger.info(f"   Search criteria: {request_data}")
        
        # Build search criteria with ALL filters
        criteria = {}
        
        # Age range
        if 'age_range' in request_data:
            criteria['age_range'] = request_data['age_range']
        
        # Fame rating
        if 'fame_rating' in request_data:
            criteria['fame_rating'] = request_data['fame_rating']
        
        # Location (city/country)
        if 'location' in request_data:
            criteria['location'] = request_data['location']
        
        # Coordinates (latitude/longitude with radius)
        if 'coordinates' in request_data:
            criteria['coordinates'] = request_data['coordinates']
            criteria['distance'] = request_data['coordinates'].get('distance', 100)
        
        # Interests/tags
        if 'interests' in request_data and request_data['interests']:
            criteria['interests'] = request_data['interests']
            criteria['interests_match_mode'] = request_data.get('interests_match_mode', 'OR')
        
        # Gender filter
        if 'gender' in request_data and request_data['gender']:
            criteria['gender'] = request_data['gender']
        
        # Execute search
        logger.info(f"   Executing search with criteria: {criteria}")
        matching_usernames = search_crud.search_users(criteria)
        logger.info(f"   ✅ Search returned {len(matching_usernames)} usernames")
        
        # Filter out current user and blocked users
        matching_usernames = [
            username for username in matching_usernames 
            if username != user_crud.get_username_by_id(g.user_id)
        ]
        
        # Get current user's location for distance calculation
        user_location = location_crud.get_user_location(g.user_id)
        user_tags = set(profile_crud.get_user_interests(g.user_id))
        
        # Build detailed profile data for each result
        results = []
        for username in matching_usernames:
            try:
                user_data = user_crud.get_user_by_username(username)
                if not user_data:
                    continue
                
                other_user_id = user_data['id']
                
                # Check if blocked (both directions)
                interaction = Interactions(connection_pool, g.user_id, other_user_id)
                if interaction.is_blocked() or interaction.did_i_block():
                    continue
                
                # Get full profile data
                profile_data = get_profile_data(connection_pool, other_user_id)
                
                # Calculate distance if both users have GPS coordinates
                distance = None
                other_location = location_crud.get_user_location(other_user_id)
                if user_location and other_location:
                    if user_location.get('latitude') and user_location.get('longitude') and \
                       other_location.get('latitude') and other_location.get('longitude'):
                        distance_data = location_crud.calculate_distance(g.user_id, other_user_id)
                        if distance_data:
                            distance = round(distance_data.get('distance_km', 0), 1)
                
                # Calculate common interests
                other_tags = set(profile_data.get('tags', []))
                common_interests_count = len(user_tags.intersection(other_tags))
                
                # Build result object
                result = {
                    'username': username,
                    'first_name': profile_data.get('first_name'),
                    'last_name': profile_data.get('last_name'),
                    'age': profile_data.get('age'),
                    'gender': profile_data.get('gender'),
                    'bio': profile_data.get('bio'),
                    'profile_picture': profile_data.get('profile_picture'),
                    'fame_rating': profile_data.get('fame_rating'),
                    'city': profile_data.get('city'),
                    'country': profile_data.get('country'),
                    'distance': distance,
                    'common_interests': common_interests_count,
                    'interests': profile_data.get('tags', [])
                }
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing search result for {username}: {e}")
                continue
        
        # Apply sorting if requested
        sort_by = request_data.get('sort_by', 'fame_rating')
        sort_order = request_data.get('sort_order', 'desc')
        reverse = sort_order == 'desc'
        
        logger.info(f"   Sorting {len(results)} results by {sort_by} ({sort_order})")
        
        # Sort key mapping
        sort_key_map = {
            'age': lambda x: x.get('age', 0),
            'fame_rating': lambda x: x.get('fame_rating', 0),
            'distance': lambda x: x.get('distance') if x.get('distance') is not None else float('inf'),
            'interests': lambda x: x.get('common_interests', 0),
            'city': lambda x: (x.get('city') or '').lower(),
            'country': lambda x: (x.get('country') or '').lower()
        }
        
        sort_key = sort_key_map.get(sort_by, sort_key_map['fame_rating'])
        results.sort(key=sort_key, reverse=reverse)
        
        logger.info(f"   ✅ Returning {len(results)} search results (filtered and sorted)")
        
        return jsonify({
            "results": results,
            "count": len(results),
            "criteria": request_data,
            "message": f"Found {len(results)} users matching your criteria"
        }), 200
        
    except Exception as e:
        logger.exception("Error in basic search endpoint")
        return jsonify({"error": str(e)}), 500


@search_bp.route("/filters", methods=["GET"])
@auth_guard
def get_search_filters():
    """
    Get available filter options for advanced search
    
    Returns available options for:
    - Age range (min/max in system)
    - Fame rating range
    - Available interests/tags
    - Available cities
    - Available countries
    - Available genders
    """
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        
        conn = connection_pool.getconn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get all available tags
                cursor.execute("SELECT DISTINCT tag_name FROM tags ORDER BY tag_name")
                tags_result = cursor.fetchall()
                available_interests = [row['tag_name'] for row in tags_result] if tags_result else []
                
                # Get age range
                cursor.execute("SELECT MIN(age) as min_age, MAX(age) as max_age FROM profiles WHERE age IS NOT NULL")
                age_result = cursor.fetchone()
                age_range = {
                    'min': age_result['min_age'] if age_result and age_result['min_age'] else 18,
                    'max': age_result['max_age'] if age_result and age_result['max_age'] else 100
                }
                
                # Get fame rating range
                cursor.execute("SELECT MIN(fame_rating) as min_fame, MAX(fame_rating) as max_fame FROM profiles WHERE fame_rating IS NOT NULL")
                fame_result = cursor.fetchone()
                fame_range = {
                    'min': fame_result['min_fame'] if fame_result and fame_result['min_fame'] else 0,
                    'max': fame_result['max_fame'] if fame_result and fame_result['max_fame'] else 100
                }
                
                # Get available cities
                cursor.execute("SELECT DISTINCT city FROM user_locations WHERE city IS NOT NULL AND city != '' ORDER BY city")
                cities_result = cursor.fetchall()
                available_cities = [row['city'] for row in cities_result] if cities_result else []
                
                # Get available countries
                cursor.execute("SELECT DISTINCT country FROM user_locations WHERE country IS NOT NULL AND country != '' ORDER BY country")
                countries_result = cursor.fetchall()
                available_countries = [row['country'] for row in countries_result] if countries_result else []
                
                # Available genders
                available_genders = ['male', 'female', 'other']
        except Exception:
            raise
        finally:
            connection_pool.putconn(conn)
        
        return jsonify({
            'available_interests': available_interests,
            'age_range': age_range,
            'fame_range': fame_range,
            'available_cities': available_cities,
            'available_countries': available_countries,
            'available_genders': available_genders,
            'interests_match_modes': ['OR', 'AND']
        }), 200
        
    except Exception as e:
        logger.exception("Error getting search filters")
        return jsonify({"error": str(e)}), 500


@search_bp.route("/filter", methods=["POST"])
@auth_guard
def filter_users():
    """
    Filter an existing list of usernames based on criteria (backend filtering)
    
    This endpoint allows filtering a pre-existing result set without re-querying
    the entire database. Useful for refining large result sets efficiently.
    
    Request Body (JSON):
    {
        "usernames": ["user1", "user2", "user3", ...],  // required - list to filter
        "age_range": {
            "min_age": 18,      // optional
            "max_age": 99       // optional
        },
        "location": {
            "city": "Paris",    // optional - partial match supported
            "country": "France" // optional - partial match supported
        },
        "coordinates": {
            "latitude": 48.8566,   // optional - GPS coordinates for radius search
            "longitude": 2.3522,
            "distance": 50         // optional - radius in km (default: 100)
        },
        "interests": ["Music", "Travel"],  // optional - interest tags
        "interests_match_mode": "OR",      // optional - "AND" or "OR" (default: "OR")
        "fame_rating": {
            "min": 0,           // optional
            "max": 100          // optional
        },
        "gender": "female"      // optional - filter by gender
    }
    
    Returns:
        JSON with list of filtered usernames
    """
    try:
        request_data = request.json
        if not request_data:
            return jsonify({"error": "Request body must be JSON"}), 400
        
        # Validate usernames list
        if 'usernames' not in request_data or not isinstance(request_data['usernames'], list):
            return jsonify({"error": "'usernames' field is required and must be a list"}), 400
        
        if len(request_data['usernames']) == 0:
            return jsonify({"error": "'usernames' list cannot be empty"}), 400
        
        usernames_list = request_data['usernames']
        
        # Validate search criteria (reuse existing validator)
        criteria_data = {k: v for k, v in request_data.items() if k != 'usernames'}
        is_valid, error_message = validate_search_data(criteria_data)
        if not is_valid:
            return jsonify({"error": error_message}), 400
        
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        
        search_crud = Search(connection_pool, filter=True)  # Enable filter mode
        
        logger.info(f"🔍 Filter requested by user_id: {g.user_id}")
        logger.info(f"   Input: {len(usernames_list)} usernames")
        logger.info(f"   Criteria: {criteria_data}")
        
        # Build criteria for filter_users method
        criteria = {}
        
        # Age range
        if 'age_range' in request_data:
            criteria['age_range'] = request_data['age_range']
        
        # Location (city/country)
        if 'location' in request_data:
            criteria['location'] = request_data['location']
        
        # Coordinates (latitude/longitude with radius)
        if 'coordinates' in request_data:
            criteria['coordinates'] = request_data['coordinates']
            criteria['distance'] = request_data['coordinates'].get('distance', 100)
        
        # Interests/tags
        if 'interests' in request_data and request_data['interests']:
            criteria['interests'] = request_data['interests']
            criteria['interests_match_mode'] = request_data.get('interests_match_mode', 'OR')
        
        # Fame rating
        if 'fame_rating' in request_data:
            criteria['fame_rating'] = request_data['fame_rating']
        
        # Gender filter
        if 'gender' in request_data:
            criteria['gender'] = request_data['gender']
        
        # Execute filter
        filtered_usernames = search_crud.filter_users(usernames_list, criteria)
        logger.info(f"   ✅ Filter returned {len(filtered_usernames)} usernames")
        
        return jsonify({
            "usernames": filtered_usernames,
            "count": len(filtered_usernames),
            "original_count": len(usernames_list),
            "criteria": criteria_data,
            "message": f"Filtered {len(usernames_list)} users down to {len(filtered_usernames)}"
        }), 200
        
    except Exception as e:
        logger.exception("Error in filter endpoint")
        return jsonify({"error": str(e)}), 500


@search_bp.route("/filter-and-sort", methods=["POST"])
@auth_guard
def filter_and_sort():
    """
    Filter AND sort an existing list of usernames in one request
    
    This endpoint provides a flexible workflow: filter first, then sort the filtered results.
    More efficient than making separate API calls for filtering and sorting.
    
    Request Body (JSON):
    {
        "usernames": ["user1", "user2", ...],  // required - list to filter
        
        // Filter criteria (all optional)
        "age_range": {
            "min_age": 18,
            "max_age": 99
        },
        "location": {
            "city": "Paris",
            "country": "France"
        },
        "coordinates": {
            "latitude": 48.8566,
            "longitude": 2.3522,
            "distance": 50
        },
        "interests": ["Music", "Travel"],
        "interests_match_mode": "OR",
        "fame_rating": {
            "min": 0,
            "max": 100
        },
        "gender": "female",
        
        // Sort criteria (optional)
        "sort_by": "fame_rating",  // age, fame_rating, interests, city, country, location
        "sort_order": "desc",      // asc or desc
        "tags": ["Music", "Art"],  // optional, for interest sorting
        "max_distance_km": 100     // optional, for location sorting
    }
    
    Returns:
        JSON with sorted list of filtered usernames with full profile data
    """
    try:
        request_data = request.json
        if not request_data:
            return jsonify({"error": "Request body must be JSON"}), 400
        
        # Validate usernames list
        if 'usernames' not in request_data or not isinstance(request_data['usernames'], list):
            return jsonify({"error": "'usernames' field is required and must be a list"}), 400
        
        if len(request_data['usernames']) == 0:
            return jsonify({"error": "'usernames' list cannot be empty"}), 400
        
        usernames_list = request_data['usernames']
        connection_pool = current_app.config["CONNECTION_POOL"]
        
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        
        logger.info(f"🔍 Filter-and-sort requested by user_id: {g.user_id}")
        logger.info(f"   Input: {len(usernames_list)} usernames")
        
        # Step 1: Filter (if filter criteria provided)
        filter_criteria_keys = ['age_range', 'location', 'coordinates', 'interests', 
                                'interests_match_mode', 'fame_rating', 'gender']
        has_filter_criteria = any(key in request_data for key in filter_criteria_keys)
        
        filtered_usernames = usernames_list
        
        if has_filter_criteria:
            # Build filter criteria
            filter_criteria = {}
            for key in filter_criteria_keys:
                if key in request_data:
                    filter_criteria[key] = request_data[key]
            
            if 'coordinates' in request_data and 'distance' in request_data['coordinates']:
                filter_criteria['distance'] = request_data['coordinates']['distance']
            
            # Validate filter criteria
            is_valid, error_message = validate_search_data(filter_criteria)
            if not is_valid:
                return jsonify({"error": f"Invalid filter criteria: {error_message}"}), 400
            
            # Apply filter
            search_crud = Search(connection_pool, filter=True)
            filtered_usernames = search_crud.filter_users(usernames_list, filter_criteria)
            logger.info(f"   ✅ Filtered: {len(usernames_list)} → {len(filtered_usernames)} usernames")
        else:
            logger.info(f"   No filter criteria, skipping filter step")
        
        # If no results after filtering, return empty
        if len(filtered_usernames) == 0:
            return jsonify({
                "usernames": [],
                "count": 0,
                "original_count": len(usernames_list),
                "message": "No users match the filter criteria"
            }), 200
        
        # Step 2: Sort (if sort criteria provided)
        sort_by = request_data.get('sort_by')
        sort_order = request_data.get('sort_order', 'desc')
        
        sorted_usernames = filtered_usernames
        
        if sort_by:
            # Build sort request
            sort_request = {
                "sort_by": sort_by,
                "order": sort_order,
                "usernames": filtered_usernames
            }
            
            # Add optional sort parameters
            if 'tags' in request_data:
                sort_request['tags'] = request_data['tags']
            if 'max_distance_km' in request_data:
                sort_request['max_distance_km'] = request_data['max_distance_km']
            
            # Validate sort criteria
            from utils.validate_sort_data import validate_sort_data
            is_valid, error_message = validate_sort_data(sort_request)
            if not is_valid:
                return jsonify({"error": f"Invalid sort criteria: {error_message}"}), 400
            
            # Apply sort
            search_crud = Search(connection_pool)
            sorted_usernames = search_crud.sort_users(sort_request, g.user_id)
            logger.info(f"   ✅ Sorted by {sort_by} ({sort_order})")
        else:
            logger.info(f"   No sort criteria, returning filtered results unsorted")
        
        return jsonify({
            "usernames": sorted_usernames,
            "count": len(sorted_usernames),
            "original_count": len(usernames_list),
            "filtered": has_filter_criteria,
            "sorted": sort_by is not None,
            "message": f"Filtered {len(usernames_list)} users down to {len(sorted_usernames)}" + 
                      (f" and sorted by {sort_by}" if sort_by else "")
        }), 200
        
    except Exception as e:
        logger.exception("Error in filter-and-sort endpoint")
        return jsonify({"error": str(e)}), 500
