import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))

from database.crud.location_crud import Location
from database.crud.user_crud import User
from database.crud.profile_crud import Profile
from database.crud.interactions_crud import Interactions
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Filter by sexual preferences - MUTUAL COMPATIBILITY
# ---------------------------------------------------------------------------
def filter_by_preferences(users, user_preferences, user_gender):
    """
    Filter users based on MUTUAL sexual preferences (both directions):
      - Current user must be interested in candidate's gender
      - Candidate must be interested in current user's gender
    This ensures true mutual compatibility for dating matches.

    Args:
        users: List of user profile dicts with 'user_id', 'gender', and 'sexual_preferences' keys
        user_preferences: String - Current user's preferences
        user_gender: String - Current user's gender

    Returns:
        List of user_ids that match BOTH directions
    """
    logger.debug(f"   Filtering by mutual preferences: user_gender='{user_gender}', user_preferences='{user_preferences}'")

    def normalize_gender(gender_value):
        """Normalize gender value to canonical form: male, female, or other."""
        if not gender_value:
            return None
        g = str(gender_value).lower().strip()
        if g in ('male', 'man', 'men', 'm'):
            return 'male'
        elif g in ('female', 'woman', 'women', 'f'):
            return 'female'
        return 'other'

    def normalize_preference(pref_value):
        """Normalize preference value to canonical form: male, female, or both."""
        if not pref_value:
            return None
        p = str(pref_value).lower().strip()
        if p in ('male', 'man', 'men', 'm'):
            return 'male'
        elif p in ('female', 'woman', 'women', 'f'):
            return 'female'
        elif p in ('both', 'bisexual', 'all', 'everyone', 'bi'):
            return 'both'
        return None

    # Normalize current user's values
    user_gender_norm = normalize_gender(user_gender)
    user_pref_norm = normalize_preference(user_preferences)

    logger.info(f"   🔍 FILTER_BY_PREFERENCES - Normalized values:")
    logger.info(f"      User gender: '{user_gender}' → '{user_gender_norm}'")
    logger.info(f"      User preferences: '{user_preferences}' → '{user_pref_norm}'")

    filtered_ids = []
    for candidate in users:
        if not candidate:
            logger.debug(f"      ⚠️  Skipping null candidate")
            continue

        candidate_id = candidate.get('user_id')
        candidate_gender_raw = candidate.get('gender')
        candidate_pref_raw = candidate.get('sexual_preferences')

        if not candidate_gender_raw:
            logger.debug(f"      ⚠️  Skipping user {candidate_id}: no gender set")
            continue

        # Normalize candidate's values
        candidate_gender_norm = normalize_gender(candidate_gender_raw)
        candidate_pref_norm = normalize_preference(candidate_pref_raw)

        logger.info(f"      🔎 Checking candidate {candidate_id}:")
        logger.info(f"         Gender: '{candidate_gender_raw}' → '{candidate_gender_norm}'")
        logger.info(f"         Preferences: '{candidate_pref_raw}' → '{candidate_pref_norm}'")

        # Check 1: Does current user want this candidate?
        # Default behavior: if preferences not specified, treat as bisexual (interested in all genders)
        user_wants_candidate = False
        if not user_pref_norm or user_pref_norm == 'both':
            user_wants_candidate = True
            logger.info(f"         ✓ User wants candidate: YES (user pref is 'both' or not specified - defaults to bisexual)")
        elif user_pref_norm == 'male' and candidate_gender_norm == 'male':
            user_wants_candidate = True
            logger.info(f"         ✓ User wants candidate: YES (user wants males, candidate is male)")
        elif user_pref_norm == 'female' and candidate_gender_norm == 'female':
            user_wants_candidate = True
            logger.info(f"         ✓ User wants candidate: YES (user wants females, candidate is female)")
        else:
            logger.info(f"         ✗ User wants candidate: NO (user pref={user_pref_norm}, candidate gender={candidate_gender_norm})")

        # Check 2: Does candidate want the current user?
        # Default behavior: if preferences not specified, treat as bisexual (interested in all genders)
        candidate_wants_user = False
        if not candidate_pref_norm or candidate_pref_norm == 'both':
            candidate_wants_user = True
            logger.info(f"         ✓ Candidate wants user: YES (candidate pref is 'both' or not specified - defaults to bisexual)")
        elif candidate_pref_norm == 'male' and user_gender_norm == 'male':
            candidate_wants_user = True
            logger.info(f"         ✓ Candidate wants user: YES (candidate wants males, user is male)")
        elif candidate_pref_norm == 'female' and user_gender_norm == 'female':
            candidate_wants_user = True
            logger.info(f"         ✓ Candidate wants user: YES (candidate wants females, user is female)")
        else:
            logger.info(f"         ✗ Candidate wants user: NO (candidate pref={candidate_pref_norm}, user gender={user_gender_norm})")

        # Only include if both want each other
        if user_wants_candidate and candidate_wants_user:
            filtered_ids.append(candidate['user_id'])
            logger.info(f"         ✅ MUTUAL MATCH FOUND - Adding to results")
        else:
            logger.info(f"         ❌ NO MUTUAL MATCH - Excluding from results")

    logger.info(f"   📊 FILTER_BY_PREFERENCES SUMMARY:")
    logger.info(f"      Total candidates checked: {len(users)}")
    logger.info(f"      Mutual matches found: {len(filtered_ids)}")
    if filtered_ids:
        logger.info(f"      Matched user IDs: {filtered_ids}")

    return filtered_ids

# ---------------------------------------------------------------------------
# Distance calculation
# ---------------------------------------------------------------------------
def calculate_distance(connection_pool, user_id, filtered_usernames):
    """
    Calculate distances to nearby users using PostGIS.
    Returns users within 50km radius who have GPS coordinates set.
    """
    try:
        location_crud = Location(connection_pool=connection_pool)

        # Check if current user has GPS coordinates
        user_location = location_crud.get_user_location(user_id)
        if not user_location or not user_location.get('latitude') or not user_location.get('longitude'):
            logger.warning(f"   Cannot calculate distances: user {user_id} has no GPS coordinates")
            return []

        # Find nearby users within 50km
        nearby_users = location_crud.find_nearby_users(user_id, 50, usernames=filtered_usernames)
        if nearby_users:
            logger.debug(f"   Found {len(nearby_users)} users with GPS coordinates within 50km")
        else:
            logger.debug(f"   No users found within 50km (or other users lack GPS coordinates)")
        return nearby_users if nearby_users else []
    except Exception as e:
        logger.error(f"   Error calculating distance: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []

# ---------------------------------------------------------------------------
# Match scoring
# ---------------------------------------------------------------------------
def calculate_match_score(user_data, candidate_data, nearby_users):
    """
    Calculate match score between user and candidate based on:
    1. Geography (40%) - Prioritize same geographic area
    2. Common tags (40%) - Maximum common interests
    3. Fame rating (20%) - Maximum fame rating
    """
    # Weights according to subject priorities
    weights = {
        'geography': 0.4,
        'tags': 0.4,
        'fame': 0.2
    }

    # Geography score (binary: in range or not)
    geo_score = 1.0 if candidate_data['username'] in nearby_users else 0.0

    # Tags score (Jaccard similarity)
    user_tags = user_data["user_tags"] if isinstance(user_data["user_tags"], set) else set(user_data["user_tags"])
    candidate_tags = candidate_data["user_tags"] if isinstance(candidate_data["user_tags"], set) else set(candidate_data["user_tags"])
    common_tags = user_tags.intersection(candidate_tags)
    all_tags = user_tags.union(candidate_tags)
    tag_score = len(common_tags) / max(len(all_tags), 1)

    # Fame score (normalized 0–1)
    fame_score = min(candidate_data["fame_rating"] / 100.0, 1.0)

    # Weighted combination
    total_score = (
        geo_score * weights['geography'] +
        tag_score * weights['tags'] + 
        fame_score * weights['fame']
    )
    return total_score

# ---------------------------------------------------------------------------
# Main matching algorithm
# ---------------------------------------------------------------------------
def matching_suggestions(connection_pool, user_id):
    logger.info(f"🔍 matching_suggestions called for user_id: {user_id}")
    user_crud = User(connection_pool=connection_pool)
    profile_crud = Profile(connection_pool=connection_pool)
    location_crud = Location(connection_pool=connection_pool)

    # Avoid circular import
    from database.crud.matching_operations_crud import Matching
    matching_crud = Matching(connection_pool)

    # Get current user's profile
    user_profile = profile_crud.get_profile_by_user_id(user_id)
    if not user_profile:
        logger.error(f"❌ User profile not found for user_id: {user_id}")
        raise ValueError("User profile not found")

    logger.info(f"   Current user profile: gender={user_profile.get('gender')}, age={user_profile.get('age')}, preferences={user_profile.get('sexual_preferences')}")

    # Get current user's location
    user_location = location_crud.get_user_location(user_id)
    if user_location and user_location.get('latitude'):
        logger.info(f"   Current user location: {user_location.get('city')}, {user_location.get('country')} ({user_location.get('latitude')}, {user_location.get('longitude')})")
    else:
        logger.warning(f"   ⚠️  Current user has NO GPS coordinates set (city/country: {user_location.get('city') if user_location else 'None'})")

    # Get all other users
    users = [user for user in user_crud.get_all_users() if user['id'] != user_id]
    logger.info(f"   Total other users in database: {len(users)}")

    # Fetch their profiles
    user_profiles = [profile_crud.get_profile_by_user_id(user['id']) for user in users]
    user_profiles = [p for p in user_profiles if p]  # remove missing profiles
    logger.info(f"   Users with complete profiles: {len(user_profiles)}")

    # Filter by preferences
    filtered_ids = filter_by_preferences(
        user_profiles,
        user_profile.get("sexual_preferences"),
        user_profile.get("gender")
    )
    logger.info(f"   After MUTUAL sexual preference filter: {len(filtered_ids)} users")
    if len(filtered_ids) < len(user_profiles):
        logger.info(f"      Filtered out {len(user_profiles) - len(filtered_ids)} users due to sexual preferences")

    # Exclude blocked users (both directions: users I blocked and users who blocked me)
    original_count = len(filtered_ids)
    def is_user_blocked(uid):
        interaction = Interactions(connection_pool, user_id, uid)
        # Check if I blocked them OR they blocked me
        return interaction.did_i_block() or interaction.is_blocked()
    
    filtered_ids = [uid for uid in filtered_ids if not is_user_blocked(uid)]
    logger.info(f"   After blocking filter: {len(filtered_ids)} users")
    if len(filtered_ids) < original_count:
        logger.info(f"      Filtered out {original_count - len(filtered_ids)} blocked users (both directions)")

    # Exclude matched users
    matched_user_ids = matching_crud.get_matched_users(user_id)
    original_count = len(filtered_ids)
    filtered_ids = [uid for uid in filtered_ids if uid not in matched_user_ids]
    logger.info(f"   After removing matched users: {len(filtered_ids)} users")
    if len(filtered_ids) < original_count:
        logger.info(f"      Filtered out {original_count - len(filtered_ids)} already matched users")
    
    # Exclude users we've already liked (but haven't matched yet)
    interactions_crud = Interactions(connection_pool, user_id, None)
    liked_user_ids = interactions_crud.get_user_likes(user_id)
    original_count = len(filtered_ids)
    filtered_ids = [uid for uid in filtered_ids if uid not in liked_user_ids]
    logger.info(f"   After removing already liked users: {len(filtered_ids)} users")
    if len(filtered_ids) < original_count:
        logger.info(f"      Filtered out {original_count - len(filtered_ids)} users you've already liked")

    if not filtered_ids:
        logger.warning(f"   ⚠️  No compatible users found after filtering!")
        logger.warning(f"      Current user preferences: {user_profile.get('sexual_preferences')}")
        logger.warning(f"      Current user gender: {user_profile.get('gender')}")
        return []

    # Build usernames for distance calculation
    filtered_usernames = [user_crud.get_user_by('id', uid, 'username')['username'] for uid in filtered_ids]
    logger.info(f"   Compatible users: {filtered_usernames}")

    # Calculate nearby users
    nearby_usernames = []
    if user_location and user_location.get('latitude'):
        try:
            nearby_users = calculate_distance(connection_pool, user_id, filtered_usernames)
            nearby_usernames = [user['username'] for user in nearby_users] if nearby_users else []
            logger.info(f"   Nearby users (within 50km): {len(nearby_usernames)}")
            if nearby_usernames:
                logger.info(f"      Nearby: {nearby_usernames}")
            else:
                logger.warning(f"      ⚠️  No users found within 50km radius")
        except Exception as e:
            logger.error(f"   ❌ Error calculating distances: {e}")
            nearby_usernames = []
    else:
        logger.warning(f"   ⚠️  Cannot calculate distances - current user has no GPS coordinates")
        logger.warning(f"      All users will have geography score = 0")

    # Prepare current user data
    user_interests = profile_crud.get_user_interests(user_id)
    user_data = {
        "username": user_crud.get_user_by('id', user_id, 'username')['username'],
        "user_tags": set(user_interests),
        "fame_rating": user_profile['fame_rating']
    }
    logger.info(f"   Current user interests: {len(user_interests)} tags - {list(user_interests)[:5]}{'...' if len(user_interests) > 5 else ''}")

    # Build candidate data and compute scores
    suggested_users = {}
    for uid in filtered_ids:
        profile_data = profile_crud.get_profile_by_user_id(uid)
        username = user_crud.get_user_by('id', uid, 'username')['username']
        user_tags = profile_crud.get_user_interests(uid)
        candidate_data = {
            "username": username,
            "user_tags": set(user_tags),
            "fame_rating": profile_data['fame_rating']
        }
        score = calculate_match_score(user_data, candidate_data, nearby_usernames)
        suggested_users[username] = score
        logger.info(f"      {username}: score={score:.3f} (fame={profile_data['fame_rating']}, common_tags={len(user_data['user_tags'].intersection(candidate_data['user_tags']))}, nearby={'YES' if username in nearby_usernames else 'NO'})")

    # Sort suggestions
    sorted_suggestions = sorted(suggested_users.items(), key=lambda item: item[1], reverse=True)
    logger.info(f"   ✅ Returning {len(sorted_suggestions)} sorted suggestions")
    if sorted_suggestions:
        logger.info(f"      Top 3: {[(u, round(s*100, 1)) for u, s in sorted_suggestions[:3]]}")

    return sorted_suggestions
