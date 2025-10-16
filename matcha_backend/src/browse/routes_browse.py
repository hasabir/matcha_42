from flask import Blueprint, request, jsonify, current_app, g
from database.crud.user_crud import User
from database.crud.profile_crud import Profile
from database.crud.location_crud import Location
from database.crud.interactions_crud import Interactions
from src.browse import browse_bp
from utils.security import auth_guard
from utils.profile_utils import get_profile_data
from utils.matching_algo import matching_suggestions, filter_by_preferences, calculate_distance
import logging

logger = logging.getLogger(__name__)


@browse_bp.route("/suggestions", methods=["GET"])
@auth_guard
def get_suggestions():
    '''Get profile suggestions based on matching algorithm with optional filters
    
    Query Parameters:
        - min_age: Minimum age filter
        - max_age: Maximum age filter
        - max_distance: Maximum distance in km (default: 50)
        - min_fame: Minimum fame rating
        - max_fame: Maximum fame rating
        - common_tags: Comma-separated tags to filter by
        - sort_by: Sort criteria (match_score, distance, age, fame_rating, common_tags)
        - sort_order: Sort order (asc, desc - default: desc)
    '''
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        # Get query parameters
        filters = {
            'min_age': request.args.get('min_age', type=int),
            'max_age': request.args.get('max_age', type=int),
            'max_distance': request.args.get('max_distance', default=50, type=int),
            'min_fame': request.args.get('min_fame', type=int),
            'max_fame': request.args.get('max_fame', type=int),
            'common_tags': request.args.get('common_tags', ''),
            'sort_by': request.args.get('sort_by', 'match_score'),
            'sort_order': request.args.get('sort_order', 'desc')
        }

        user_crud = User(connection_pool)
        profile_crud = Profile(connection_pool)
        location_crud = Location(connection_pool)

        # Get current user's profile and location
        user_profile = profile_crud.get_profile_by_user_id(g.user_id)
        if not user_profile:
            return jsonify({"error": "User profile not found"}), 404

        user_location = location_crud.get_user_location(g.user_id)
        user_tags = set(profile_crud.get_user_interests(g.user_id))

        # Get base matching suggestions
        suggested_users = matching_suggestions(connection_pool, g.user_id)
        
        if not suggested_users:
            return jsonify({"suggestions": []}), 200

        # Build detailed profile data for each suggestion
        suggestions = []
        
        for username, match_score in suggested_users:
            try:
                # Get user data
                user_data = user_crud.get_user_by_username(username)
                if not user_data:
                    continue

                other_user_id = user_data['id']
                
                # Check if blocked
                if Interactions(connection_pool, g.user_id, other_user_id).is_blocked():
                    continue

                # Get profile data
                profile_data = get_profile_data(connection_pool, other_user_id)
                
                # Apply age filter
                if filters['min_age'] and profile_data.get('age', 0) < filters['min_age']:
                    continue
                if filters['max_age'] and profile_data.get('age', 0) > filters['max_age']:
                    continue

                # Apply fame rating filter
                fame = profile_data.get('fame_rating', 0)
                if filters['min_fame'] and fame < filters['min_fame']:
                    continue
                if filters['max_fame'] and fame > filters['max_fame']:
                    continue

                # Calculate distance
                distance = None
                other_location = location_crud.get_user_location(other_user_id)
                if user_location and other_location:
                    # Calculate distance using PostGIS
                    distance_data = location_crud.calculate_distance(
                        g.user_id, 
                        other_user_id
                    )
                    if distance_data:
                        distance = round(distance_data.get('distance_km', 0), 1)

                # Apply distance filter
                if distance and filters['max_distance'] and distance > filters['max_distance']:
                    continue

                # Calculate common interests
                other_tags = set(profile_data.get('tags', []))
                common_interests_set = user_tags.intersection(other_tags)
                common_interests_count = len(common_interests_set)

                # Apply common tags filter
                if filters['common_tags']:
                    required_tags = set(tag.strip() for tag in filters['common_tags'].split(','))
                    if not required_tags.intersection(other_tags):
                        continue

                # Prepare suggestion data
                suggestion = {
                    'username': username,
                    'first_name': profile_data.get('first_name'),
                    'last_name': profile_data.get('last_name'),
                    'age': profile_data.get('age'),
                    'gender': profile_data.get('gender'),
                    'bio': profile_data.get('bio'),
                    'profile_picture': profile_data.get('profile_picture'),
                    'fame_rating': fame,
                    'city': profile_data.get('city'),
                    'country': profile_data.get('country'),
                    'distance': distance,
                    'match_score': round(match_score * 100, 1),  # Convert to percentage
                    'common_interests': common_interests_count,
                    'interests': profile_data.get('tags', []),
                    'compatibility_reasons': []
                }

                # Add compatibility reasons
                if distance and distance < 10:
                    suggestion['compatibility_reasons'].append(f"Very close - only {distance}km away!")
                elif distance and distance < 50:
                    suggestion['compatibility_reasons'].append(f"Nearby - {distance}km away")
                
                if common_interests_count >= 5:
                    suggestion['compatibility_reasons'].append(f"Shares {common_interests_count} interests with you!")
                elif common_interests_count >= 3:
                    suggestion['compatibility_reasons'].append(f"{common_interests_count} common interests")
                
                if fame > 80:
                    suggestion['compatibility_reasons'].append("Highly popular profile!")
                
                suggestions.append(suggestion)

            except Exception as e:
                logger.error(f"Error processing suggestion for {username}: {e}")
                continue

        # Sort suggestions
        sort_key_map = {
            'match_score': lambda x: x.get('match_score', 0),
            'distance': lambda x: x.get('distance', float('inf')),
            'age': lambda x: x.get('age', 0),
            'fame_rating': lambda x: x.get('fame_rating', 0),
            'common_tags': lambda x: x.get('common_interests', 0)
        }

        sort_key = sort_key_map.get(filters['sort_by'], sort_key_map['match_score'])
        reverse = filters['sort_order'] == 'desc'
        
        suggestions.sort(key=sort_key, reverse=reverse)

        return jsonify({
            "suggestions": suggestions,
            "count": len(suggestions),
            "filters_applied": filters
        }), 200

    except Exception as e:
        logger.exception("Error generating suggestions")
        return jsonify({"error": str(e)}), 500
