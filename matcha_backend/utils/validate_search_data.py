"""
Search data validation module
Validates search/filter criteria for user discovery
"""
import logging

logger = logging.getLogger(__name__)


def validate_search_data(search_data):
    """
    Validate search/filter data for user discovery
    
    Expected format:
    {
        "age_min": int (optional),
        "age_max": int (optional),
        "fame_rating_min": int (optional),
        "fame_rating_max": int (optional),
        "location": {
            "latitude": float,
            "longitude": float,
            "radius": int (km)
        } (optional),
        "tags": [str] (optional),
        "gender": str (optional),
        "sexual_preferences": str (optional)
    }
    
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if not search_data:
        return True, "No filters applied"  # Empty search is valid
    
    if not isinstance(search_data, dict):
        return False, "Search data must be a dictionary"
    
    # Validate age filters
    if 'age_min' in search_data:
        if not isinstance(search_data['age_min'], int) or search_data['age_min'] < 18:
            return False, "'age_min' must be an integer >= 18"
    
    if 'age_max' in search_data:
        if not isinstance(search_data['age_max'], int) or search_data['age_max'] > 100:
            return False, "'age_max' must be an integer <= 100"
    
    if 'age_min' in search_data and 'age_max' in search_data:
        if search_data['age_min'] > search_data['age_max']:
            return False, "'age_min' cannot be greater than 'age_max'"
    
    # Validate fame rating filters
    if 'fame_rating_min' in search_data:
        if not isinstance(search_data['fame_rating_min'], (int, float)) or search_data['fame_rating_min'] < 0:
            return False, "'fame_rating_min' must be a number >= 0"
    
    if 'fame_rating_max' in search_data:
        if not isinstance(search_data['fame_rating_max'], (int, float)) or search_data['fame_rating_max'] > 100:
            return False, "'fame_rating_max' must be a number <= 100"
    
    if 'fame_rating_min' in search_data and 'fame_rating_max' in search_data:
        if search_data['fame_rating_min'] > search_data['fame_rating_max']:
            return False, "'fame_rating_min' cannot be greater than 'fame_rating_max'"
    
    # Validate location filter
    if 'location' in search_data:
        location = search_data['location']
        
        if not isinstance(location, dict):
            return False, "'location' must be a dictionary"
        
        required_location_fields = ['latitude', 'longitude', 'radius']
        for field in required_location_fields:
            if field not in location:
                return False, f"'location.{field}' is required"
        
        if not isinstance(location['latitude'], (int, float)) or not (-90 <= location['latitude'] <= 90):
            return False, "'location.latitude' must be a number between -90 and 90"
        
        if not isinstance(location['longitude'], (int, float)) or not (-180 <= location['longitude'] <= 180):
            return False, "'location.longitude' must be a number between -180 and 180"
        
        if not isinstance(location['radius'], (int, float)) or location['radius'] <= 0:
            return False, "'location.radius' must be a positive number"
    
    # Validate tags filter
    if 'tags' in search_data:
        if not isinstance(search_data['tags'], list):
            return False, "'tags' must be a list"
        
        if not all(isinstance(tag, str) and tag.strip() for tag in search_data['tags']):
            return False, "'tags' must be a list of non-empty strings"
    
    # Validate gender filter
    if 'gender' in search_data:
        valid_genders = ['male', 'female', 'other']
        if search_data['gender'] not in valid_genders:
            return False, f"'gender' must be one of: {', '.join(valid_genders)}"
    
    # Validate sexual preferences filter
    if 'sexual_preferences' in search_data:
        valid_preferences = ['male', 'female', 'both']
        if search_data['sexual_preferences'] not in valid_preferences:
            return False, f"'sexual_preferences' must be one of: {', '.join(valid_preferences)}"
    
    return True, "Valid search data"
