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


@browse_bp.route("/filters", methods=["GET"])
@auth_guard
def get_filter_options():
    """Get available filter options for the browse page
    
    Returns:
        - available_interests: List of all available tags/interests
        - age_range: Min and max age in the system
        - fame_range: Min and max fame rating in the system
        - available_cities: List of cities with users
        - available_countries: List of countries with users
    """
    try:
        logger.info(f"🔍 Filter options requested by user_id: {g.user_id}")
        
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            logger.error("❌ Database connection pool is not available")
            return jsonify({"error": "Database connection pool is not available"}), 500

        profile_crud = Profile(connection_pool)
        location_crud = Location(connection_pool)
        
        # Get all available tags from database
        try:
            with connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Get all tags
                    cursor.execute("SELECT DISTINCT tag_name FROM tags ORDER BY tag_name")
                    tags_result = cursor.fetchall()
                    available_interests = [row['tag_name'] for row in tags_result] if tags_result else []
                    
                    # Get age range from profiles
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
                    
                    # Get available cities and countries
                    cursor.execute("SELECT DISTINCT city FROM locations WHERE city IS NOT NULL AND city != '' ORDER BY city")
                    cities_result = cursor.fetchall()
                    available_cities = [row['city'] for row in cities_result] if cities_result else []
                    
                    cursor.execute("SELECT DISTINCT country FROM locations WHERE country IS NOT NULL AND country != '' ORDER BY country")
                    countries_result = cursor.fetchall()
                    available_countries = [row['country'] for row in countries_result] if countries_result else []
        
        except Exception as e:
            logger.error(f"Error querying filter options: {e}")
            # Return defaults if query fails
            available_interests = [
                "Hiking", "Reading", "Cooking", "Travel", "Music", "Art",
                "Sports", "Movies", "Gaming", "Volunteering"
            ]
            age_range = {'min': 18, 'max': 100}
            fame_range = {'min': 0, 'max': 100}
            available_cities = []
            available_countries = []
        
        filter_options = {
            'available_interests': available_interests,
            'age_range': age_range,
            'fame_range': fame_range,
            'available_cities': available_cities,
            'available_countries': available_countries
        }
        
        logger.info(f"   ✅ Returning filter options: {len(available_interests)} tags, {len(available_cities)} cities, {len(available_countries)} countries")
        
        return jsonify(filter_options), 200
        
    except Exception as e:
        logger.exception("Error getting filter options")
        return jsonify({"error": str(e)}), 500


@browse_bp.route("/suggestions", methods=["GET"])
@auth_guard
def get_suggestions():
    '''Get profile suggestions based on matching algorithm with optional filters
    
    Implements all subject requirements:
    1. Only "interesting" profiles (filtered by sexual orientation)
    2. Match based on: geography (priority), common tags, fame rating
    3. Prioritize same geographical area
    4. Sortable by: age, location, fame rating, common tags, city, country
    5. Filterable by: age, location, fame rating, common tags, city, country
    
    Query Parameters:
        - min_age: Minimum age filter
        - max_age: Maximum age filter
        - max_distance: Maximum distance in km (default: 500km - wide range)
        - city: Filter by specific city name (case-insensitive)
        - country: Filter by specific country name (case-insensitive)
        - min_fame: Minimum fame rating
        - max_fame: Maximum fame rating
        - common_tags: Comma-separated tags to filter by
        - sort_by: Sort criteria (match_score, distance, age, fame_rating, common_tags, city, country)
        - sort_order: Sort order (asc, desc - default: desc)
    '''
    try:
        logger.info(f"🔍 Browse suggestions requested by user_id: {g.user_id}")
        
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            logger.error("❌ Database connection pool is not available")
            return jsonify({"error": "Database connection pool is not available"}), 500

        # Get query parameters for filtering and sorting
        filters = {
            'min_age': request.args.get('min_age', type=int),
            'max_age': request.args.get('max_age', type=int),
            'max_distance': request.args.get('max_distance', type=int),  # No default - preserve geographical priority (same city/country)
            'city': request.args.get('city', type=str),
            'country': request.args.get('country', type=str),
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
            logger.warning(f"⚠️  User {g.user_id} has no profile")
            return jsonify({"error": "User profile not found. Please complete your profile first."}), 404

        logger.info(f"   User profile: gender={user_profile.get('gender')}, age={user_profile.get('age')}, preferences={user_profile.get('sexual_preferences')}")
        
        user_location = location_crud.get_user_location(g.user_id)
        if user_location:
            logger.info(f"   User location: {user_location.get('city')}, {user_location.get('country')}")
        else:
            logger.warning(f"   ⚠️  User has no location set")
            
        user_tags = set(profile_crud.get_user_interests(g.user_id))
        logger.info(f"   User interests: {len(user_tags)} tags")

        # Get base matching suggestions (already filtered by sexual preference)
        logger.info(f"   Running matching algorithm...")
        suggested_users = matching_suggestions(connection_pool, g.user_id)
        logger.info(f"   ✅ Matching algorithm returned {len(suggested_users)} suggestions")
        
        if not suggested_users:
            logger.warning(f"   ⚠️  No matches found for user {g.user_id}")
            
            # Provide helpful diagnostic message
            diagnostic_message = "No matches found. "
            if not user_location or not user_location.get('latitude'):
                diagnostic_message += "⚠️ You haven't set your GPS location. Please use 'Use my GPS' to enable location-based matching. "
            
            # Check if there are any compatible users at all
            all_users = user_crud.get_all_users()
            other_users = [u for u in all_users if u['id'] != g.user_id]
            if len(other_users) == 0:
                diagnostic_message += "There are no other users in the system yet. "
            else:
                diagnostic_message += f"There are {len(other_users)} other users, but none match your preferences or have complete profiles with locations. Try expanding your search criteria or check back later."
            
            return jsonify({
                "suggestions": [],
                "count": 0,
                "message": diagnostic_message
            }), 200

        # Build detailed profile data for each suggestion
        suggestions = []
        
        logger.info(f"   📊 Processing {len(suggested_users)} potential matches with filters:")
        logger.info(f"      Age filter: {filters['min_age']} - {filters['max_age']}")
        logger.info(f"      Distance filter: max {filters['max_distance']} km")
        logger.info(f"      City filter: {filters['city']}")
        logger.info(f"      Country filter: {filters['country']}")
        logger.info(f"      Fame filter: {filters['min_fame']} - {filters['max_fame']}")
        logger.info(f"      Common tags filter: {filters['common_tags']}")
        
        for username, match_score in suggested_users:
            try:
                # Get user data
                user_data = user_crud.get_user_by_username(username)
                if not user_data:
                    logger.warning(f"      ⚠️  User {username} not found")
                    continue

                other_user_id = user_data['id']
                
                logger.info(f"   🔍 Processing candidate: {username} (id={other_user_id})")
                
                # Check if blocked (security check - both directions)
                interaction = Interactions(connection_pool, g.user_id, other_user_id)
                if interaction.is_blocked() or interaction.did_i_block():
                    logger.info(f"      ❌ Blocked user - skipping")
                    continue

                # Get profile data
                profile_data = get_profile_data(connection_pool, other_user_id)
                
                # Apply age filter
                user_age = profile_data.get('age', 0)
                logger.info(f"      Age: {user_age}")
                if filters['min_age'] and user_age < filters['min_age']:
                    logger.info(f"      ❌ Filtered out: age {user_age} < min {filters['min_age']}")
                    continue
                if filters['max_age'] and user_age > filters['max_age']:
                    logger.info(f"      ❌ Filtered out: age {user_age} > max {filters['max_age']}")
                    continue

                # Apply fame rating filter
                fame = profile_data.get('fame_rating', 0)
                logger.info(f"      Fame: {fame}")
                if filters['min_fame'] and fame < filters['min_fame']:
                    logger.info(f"      ❌ Filtered out: fame {fame} < min {filters['min_fame']}")
                    continue
                if filters['max_fame'] and fame > filters['max_fame']:
                    logger.info(f"      ❌ Filtered out: fame {fame} > max {filters['max_fame']}")
                    continue

                # Calculate distance (prioritize geographical area)
                distance = None
                other_location = location_crud.get_user_location(other_user_id)
                logger.info(f"      Other user location: {other_location}")
                logger.info(f"      Current user location: {user_location}")
                
                if user_location and other_location:
                    # Only calculate if both users have GPS coordinates
                    if user_location.get('latitude') and user_location.get('longitude') and \
                       other_location.get('latitude') and other_location.get('longitude'):
                        # Calculate distance using PostGIS
                        logger.info(f"      Calculating distance between users...")
                        distance_data = location_crud.calculate_distance(
                            g.user_id, 
                            other_user_id
                        )
                        logger.info(f"      Distance data returned: {distance_data}")
                        if distance_data:
                            distance = round(distance_data.get('distance_km', 0), 1)
                            logger.info(f"      ✅ Distance: {distance} km")
                            
                            # DON'T filter by distance here - let geographical priority sorting handle it first
                            # Distance filter will be applied AFTER sorting to preserve same-city/country priority
                    else:
                        logger.info(f"      ⚠️  Distance: Cannot calculate (missing GPS coordinates)")
                        logger.info(f"         User coords: lat={user_location.get('latitude')}, lon={user_location.get('longitude')}")
                        logger.info(f"         Other coords: lat={other_location.get('latitude')}, lon={other_location.get('longitude')}")
                else:
                    logger.info(f"      ⚠️  Distance: Cannot calculate (one or both users have no location)")
                    logger.info(f"         user_location exists: {bool(user_location)}")
                    logger.info(f"         other_location exists: {bool(other_location)}")

                # Apply city filter
                if filters['city']:
                    user_city = other_location.get('city', '') if other_location else ''
                    if not user_city or user_city.lower() != filters['city'].lower():
                        logger.info(f"      ❌ Filtered out: city '{user_city}' doesn't match filter '{filters['city']}'")
                        continue

                # Apply country filter
                if filters['country']:
                    user_country = other_location.get('country', '') if other_location else ''
                    if not user_country or user_country.lower() != filters['country'].lower():
                        logger.info(f"      ❌ Filtered out: country '{user_country}' doesn't match filter '{filters['country']}'")
                        continue

                # Calculate common interests (maximum common tags)
                other_tags = set(profile_data.get('tags', []))
                common_interests_set = user_tags.intersection(other_tags)
                common_interests_count = len(common_interests_set)
                logger.info(f"      Common interests: {common_interests_count}")

                # Apply common tags filter
                if filters['common_tags']:
                    required_tags = set(tag.strip() for tag in filters['common_tags'].split(','))
                    if not required_tags.intersection(other_tags):
                        logger.info(f"      ❌ Filtered out: no common tags from filter {filters['common_tags']}")
                        continue

                logger.info(f"      ✅ Passed all filters - adding to suggestions")
                
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

                # Add compatibility reasons for better UX
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

        # Sort suggestions with GEOGRAPHICAL PRIORITY
        # Per subject requirements: "Priority should be given to users within the same geographical area"
        # Strategy: Three-tier geographical priority system:
        #   - Group 0 (Highest): Users within 50km (same geographical area)
        #   - Group 1 (Medium): Users in same city OR same country (but >50km away or no GPS)
        #   - Group 2 (Lowest): Users in different area (far away and different location)
        
        logger.info(f"   📊 Sorting {len(suggestions)} suggestions with geographical priority...")
        
        # Define threshold for "same geographical area"
        SAME_AREA_THRESHOLD_KM = 50
        
        # Get current user's location for comparison
        user_city = (user_location.get('city') or '').lower() if user_location else ''
        user_country = (user_location.get('country') or '').lower() if user_location else ''
        
        logger.info(f"   Current user location: city='{user_city}', country='{user_country}'")
        
        # Define secondary sort criteria
        sort_key_map = {
            'match_score': lambda x: x.get('match_score', 0),
            'distance': lambda x: x.get('distance') if x.get('distance') is not None else float('inf'),
            'age': lambda x: x.get('age', 0),
            'fame_rating': lambda x: x.get('fame_rating', 0),
            'common_tags': lambda x: x.get('common_interests', 0),
            'city': lambda x: (x.get('city') or '').lower(),
            'country': lambda x: (x.get('country') or '').lower()
        }

        secondary_sort_key = sort_key_map.get(filters['sort_by'], sort_key_map['match_score'])
        reverse = filters['sort_order'] == 'desc'
        
        # Special handling for distance sorting (ascending makes more sense - closest first)
        if filters['sort_by'] == 'distance':
            reverse = filters['sort_order'] == 'desc'
        
        # PRIMARY SORT: Three-tier geographical priority
        def geographical_priority_sort_key(suggestion):
            """
            Returns a tuple for sorting with three-tier geographical priority:
            
            Tier 0 (Highest Priority): Same city OR within 50km
                - Same city as current user (even without GPS), OR
                - Have GPS distance AND distance <= 50km
                
            Tier 1 (Medium Priority): Same country (but different city and >50km)
                - Same country as current user
                - But different city and >50km away (or no GPS)
                
            Tier 2 (Lowest Priority): Different country
                - Different country, OR
                - No location information at all
            
            Within each tier, sort by the secondary criteria (match_score, age, etc.)
            
            Returns:
                tuple: (geographic_tier, secondary_sort_value)
            """
            distance = suggestion.get('distance')
            candidate_city = (suggestion.get('city') or '').lower()
            candidate_country = (suggestion.get('country') or '').lower()
            
            # Determine geographical tier
            geographic_tier = 2  # Default: different country (lowest priority)
            
            # Tier 0: Same city OR within 50km (highest priority)
            # City match takes precedence even without GPS
            if (user_city and candidate_city and user_city == candidate_city) or \
               (distance is not None and distance <= SAME_AREA_THRESHOLD_KM):
                geographic_tier = 0
                reason = "same city" if user_city == candidate_city else f"within {distance}km"
                logger.debug(f"      User {suggestion.get('username')}: Tier 0 ({reason})")
            
            # Tier 1: Same country but different city
            elif user_country and candidate_country and user_country == candidate_country:
                geographic_tier = 1
                logger.debug(f"      User {suggestion.get('username')}: Tier 1 (same country)")
            
            # Tier 2: Different country (default)
            else:
                logger.debug(f"      User {suggestion.get('username')}: Tier 2 (different country or no location)")
            
            # Get secondary sort value
            secondary_value = secondary_sort_key(suggestion)
            
            # For descending order, negate numeric values (for proper sorting within tier)
            if reverse and isinstance(secondary_value, (int, float)):
                secondary_value = -secondary_value
            
            return (geographic_tier, secondary_value)
        
        # Apply the geographical priority sort FIRST
        # Note: For the secondary sort within tiers, we use reverse=False because we've already
        # handled the reverse logic in the key function itself
        suggestions.sort(key=geographical_priority_sort_key, reverse=False)
        
        # NOW apply distance filter AFTER geographical priority sorting
        # CRITICAL: Preserve geographical priority - don't filter out same-city/country users
        # Per subject: "Priority should be given to users within the same geographical area"
        pre_filter_count = len(suggestions)
        if filters['max_distance']:
            # Keep users from same city/country regardless of distance, OR within max_distance
            suggestions = [
                s for s in suggestions 
                if (s.get('distance') is None or s.get('distance') <= filters['max_distance']) or
                   ((s.get('city') or '').lower() == user_city and user_city) or
                   ((s.get('country') or '').lower() == user_country and user_country)
            ]
            logger.info(f"   📏 Distance filter applied (≤{filters['max_distance']}km, preserving same city/country): {len(suggestions)}/{pre_filter_count} suggestions remain")
        
        # Log sorting results
        tier0_count = sum(1 for s in suggestions if (
            ((s.get('city') or '').lower() == user_city and user_city) or
            (s.get('distance') is not None and s.get('distance') <= SAME_AREA_THRESHOLD_KM)
        ))
        tier1_count = sum(1 for s in suggestions if (
            not ((s.get('city') or '').lower() == user_city and user_city) and
            not (s.get('distance') is not None and s.get('distance') <= SAME_AREA_THRESHOLD_KM) and
            ((s.get('country') or '').lower() == user_country and user_country)
        ))
        tier2_count = len(suggestions) - tier0_count - tier1_count
        
        logger.info(f"   ✅ Final suggestions with three-tier geographical priority:")
        logger.info(f"      Tier 0 (same city OR ≤50km): {tier0_count} users")
        logger.info(f"      Tier 1 (same country): {tier1_count} users")
        logger.info(f"      Tier 2 (different country): {tier2_count} users")

        return jsonify({
            "suggestions": suggestions,
            "count": len(suggestions),
            "filters_applied": filters,
            "message": f"Found {len(suggestions)} compatible profiles"
        }), 200

    except Exception as e:
        logger.exception("Error generating suggestions")
        return jsonify({"error": str(e), "message": "Failed to generate suggestions"}), 500


@browse_bp.route("/search/users", methods=["POST"])
@auth_guard
def advanced_search():
    """Advanced search endpoint for DiscoverPage
    
    Implements subject requirement: "Users must be able to perform an advanced search 
    by selecting one or more criteria"
    
    POST body structure:
    {
        "age_range": {"min_age": 25, "max_age": 35},
        "fame_rating": {"min": 50, "max": 100},
        "coordinates": {"latitude": 48.8566, "longitude": 2.3522, "distance": 100},
        "location": {"city": "Paris", "country": "France"},
        "interests": ["Hiking", "Reading"],
        "interests_match_mode": "OR",  // or "AND"
        "gender": "female",
        "sort_by": "fame_rating",  // age, distance, fame_rating, interests, city, country
        "sort_order": "desc"  // asc or desc
    }
    """
    try:
        logger.info(f"🔍 Advanced search requested by user_id: {g.user_id}")
        
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool unavailable"}), 500

        # Get search criteria from request body
        criteria = request.get_json() or {}
        logger.info(f"   Search criteria: {criteria}")

        user_crud = User(connection_pool)
        profile_crud = Profile(connection_pool)
        location_crud = Location(connection_pool)

        # Get current user's profile and location
        user_profile = profile_crud.get_profile_by_user_id(g.user_id)
        if not user_profile:
            return jsonify({"error": "Please complete your profile first"}), 404

        user_location = location_crud.get_user_location(g.user_id)
        user_tags = set(profile_crud.get_user_interests(g.user_id))

        # Get already liked users to exclude them from results
        interactions_crud = Interactions(connection_pool, g.user_id, None)
        liked_user_ids = interactions_crud.get_user_likes(g.user_id)
        logger.info(f"   User has already liked {len(liked_user_ids)} users - excluding them from results")

        # Get ALL users (except self) - broader than matching algorithm
        all_users = user_crud.get_all_users()
        logger.info(f"   Found {len(all_users)} total users in system")

        results = []

        for user_data in all_users:
            # Skip self
            if user_data['id'] == g.user_id:
                continue

            other_user_id = user_data['id']
            username = user_data['username']
            
            # Skip already liked users
            if other_user_id in liked_user_ids:
                logger.info(f"   ❌ Skipping {username}: already liked")
                continue

            try:
                # Skip blocked users (both directions)
                interaction = Interactions(connection_pool, g.user_id, other_user_id)
                if interaction.is_blocked() or interaction.did_i_block():
                    continue

                # Get profile data
                profile_data = get_profile_data(connection_pool, other_user_id)
                
                logger.info(f"   Checking user: {username}, age={profile_data.get('age')}, has_bio={bool(profile_data.get('bio'))}")
                
                # Ensure profile is complete (but allow profiles without first_name since username "bb bb" might be the display name)
                if not profile_data.get('bio'):
                    logger.info(f"   ❌ Skipping {username}: no bio")
                    continue

                # ========== APPLY FILTERS ==========
                
                # AGE RANGE filter
                if 'age_range' in criteria:
                    age = profile_data.get('age')
                    
                    # Skip if age is missing
                    if age is None:
                        logger.info(f"   ❌ Skipping {username}: age is None")
                        continue
                    
                    # Ensure age is an integer
                    try:
                        age = int(age)
                    except (ValueError, TypeError):
                        logger.info(f"   ❌ Skipping {username}: invalid age value {age}")
                        continue
                    
                    min_age = criteria['age_range'].get('min_age')
                    max_age = criteria['age_range'].get('max_age')
                    
                    # Convert min_age and max_age to integers
                    if min_age is not None:
                        min_age = int(min_age)
                    if max_age is not None:
                        max_age = int(max_age)
                    
                    logger.info(f"   Age filter: user {username} age={age} (type: {type(age).__name__}), range={min_age}-{max_age}")
                    
                    if min_age is not None and age < min_age:
                        logger.info(f"   ❌ Filtered out {username}: age {age} < min {min_age}")
                        continue
                    if max_age is not None and age > max_age:
                        logger.info(f"   ❌ Filtered out {username}: age {age} > max {max_age}")
                        continue
                    
                    logger.info(f"   ✅ {username} passed age filter")

                # FAME RATING filter
                if 'fame_rating' in criteria:
                    fame = profile_data.get('fame_rating', 0)
                    min_fame = criteria['fame_rating'].get('min')
                    max_fame = criteria['fame_rating'].get('max')
                    
                    if min_fame is not None and fame < min_fame:
                        continue
                    if max_fame is not None and fame > max_fame:
                        continue

                # GENDER filter
                if criteria.get('gender'):
                    if profile_data.get('gender', '').lower() != criteria['gender'].lower():
                        continue

                # Get location data
                other_location = location_crud.get_user_location(other_user_id)

                # LOCATION filter - GPS-based (coordinates)
                distance = None
                if 'coordinates' in criteria:
                    search_lat = criteria['coordinates'].get('latitude')
                    search_lng = criteria['coordinates'].get('longitude')
                    max_distance = criteria['coordinates'].get('distance', 500)
                    
                    if other_location and other_location.get('latitude') and other_location.get('longitude'):
                        # Calculate distance from search center
                        try:
                            with connection_pool.get_connection() as conn:
                                with conn.cursor() as cursor:
                                    cursor.execute("""
                                        SELECT 
                                            ST_Distance(
                                                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                                                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                                            ) / 1000 AS distance_km
                                    """, (search_lng, search_lat, other_location['longitude'], other_location['latitude']))
                                    
                                    result = cursor.fetchone()
                                    if result:
                                        distance = round(result['distance_km'], 1)
                                        
                                        # Apply distance filter
                                        if distance > max_distance:
                                            continue
                        except Exception as e:
                            logger.error(f"Error calculating distance: {e}")
                            continue
                    else:
                        # User has no GPS location - exclude from GPS-based search
                        continue

                # LOCATION filter - Text-based (city/country)
                elif 'location' in criteria:
                    city_filter = criteria['location'].get('city', '').lower()
                    country_filter = criteria['location'].get('country', '').lower()
                    
                    if city_filter or country_filter:
                        if not other_location:
                            continue
                        
                        other_city = (other_location.get('city') or '').lower()
                        other_country = (other_location.get('country') or '').lower()
                        
                        if city_filter and other_city != city_filter:
                            continue
                        if country_filter and other_country != country_filter:
                            continue

                # INTEREST TAGS filter
                other_tags = set(profile_data.get('tags', []))
                common_interests_count = len(user_tags.intersection(other_tags))
                
                if 'interests' in criteria and criteria['interests']:
                    required_tags = set(tag.lower() for tag in criteria['interests'])
                    other_tags_lower = set(tag.lower() for tag in other_tags)
                    
                    match_mode = criteria.get('interests_match_mode', 'OR')
                    
                    if match_mode == 'AND':
                        # Must have ALL required tags
                        if not required_tags.issubset(other_tags_lower):
                            continue
                    else:  # OR mode
                        # Must have at least ONE required tag
                        if not required_tags.intersection(other_tags_lower):
                            continue

                # ========== BUILD RESULT ==========
                
                logger.info(f"   ✅ {username} passed ALL filters - adding to results")
                
                result = {
                    'username': username,
                    'first_name': profile_data.get('first_name'),
                    'last_name': profile_data.get('last_name'),
                    'age': profile_data.get('age'),
                    'gender': profile_data.get('gender'),
                    'bio': profile_data.get('bio'),
                    'profile_picture': profile_data.get('profile_picture'),
                    'fame_rating': profile_data.get('fame_rating', 0),
                    'city': profile_data.get('city'),
                    'country': profile_data.get('country'),
                    'distance': distance,
                    'common_interests': common_interests_count,
                    'interests': profile_data.get('tags', [])
                }

                results.append(result)

            except Exception as e:
                logger.error(f"Error processing user {username}: {e}")
                continue

        # ========== SORT RESULTS ==========
        
        sort_by = criteria.get('sort_by', 'fame_rating')
        sort_order = criteria.get('sort_order', 'desc')
        
        sort_key_map = {
            'age': lambda x: x.get('age', 0),
            'distance': lambda x: x.get('distance') if x.get('distance') is not None else float('inf'),
            'fame_rating': lambda x: x.get('fame_rating', 0),
            'interests': lambda x: x.get('common_interests', 0),
            'city': lambda x: (x.get('city') or '').lower(),
            'country': lambda x: (x.get('country') or '').lower()
        }

        sort_key = sort_key_map.get(sort_by, sort_key_map['fame_rating'])
        reverse = sort_order == 'desc'
        
        results.sort(key=sort_key, reverse=reverse)

        logger.info(f"   ✅ Advanced search complete: {len(results)} results")
        logger.info(f"      Sorted by: {sort_by} ({sort_order})")

        return jsonify({
            "results": results,
            "count": len(results),
            "criteria": criteria
        }), 200

    except Exception as e:
        logger.exception("Error in advanced search")
        return jsonify({"error": str(e)}), 500
