"""
Search data validation module
Validates search/filter criteria for user discovery
Supports both standalone advanced search and filtered search
"""
import logging

logger = logging.getLogger(__name__)


def validate_search_data(search_data):
    """
    Validate search/filter data for user discovery
    
    Supports two formats:
    
    1. Advanced Search (POST /api/search/users):
    {
        "age_range": {
            "min_age": int (optional),
            "max_age": int (optional)
        },
        "location": {
            "city": str (optional),
            "country": str (optional)
        },
        "coordinates": {
            "latitude": float,
            "longitude": float,
            "distance": int (km, optional, default: 100)
        },
        "interests": [str] (optional),
        "interests_match_mode": "OR" | "AND" (optional, default: "OR"),
        "fame_rating": {
            "min": int (optional),
            "max": int (optional)
        },
        "gender": str (optional),
        "sort_by": str (optional),
        "sort_order": "asc" | "desc" (optional)
    }
    
    2. Legacy format (for backwards compatibility):
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
        "tags": [str] (optional)
    }
    
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if not search_data:
        return True, "No filters applied"  # Empty search is valid
    
    if not isinstance(search_data, dict):
        return False, "Search data must be a dictionary"
    
    # Validate age range (new format)
    if 'age_range' in search_data:
        age_range = search_data['age_range']
        if not isinstance(age_range, dict):
            return False, "'age_range' must be a dictionary"
        
        if 'min_age' in age_range:
            if not isinstance(age_range['min_age'], int) or age_range['min_age'] < 18:
                return False, "'age_range.min_age' must be an integer >= 18"
        
        if 'max_age' in age_range:
            if not isinstance(age_range['max_age'], int) or age_range['max_age'] > 100:
                return False, "'age_range.max_age' must be an integer <= 100"
        
        if 'min_age' in age_range and 'max_age' in age_range:
            if age_range['min_age'] > age_range['max_age']:
                return False, "'age_range.min_age' cannot be greater than 'age_range.max_age'"
    
    # Validate age filters (legacy format for backwards compatibility)
    if 'age_min' in search_data:
        if not isinstance(search_data['age_min'], int) or search_data['age_min'] < 18:
            return False, "'age_min' must be an integer >= 18"
    
    if 'age_max' in search_data:
        if not isinstance(search_data['age_max'], int) or search_data['age_max'] > 100:
            return False, "'age_max' must be an integer <= 100"
    
    if 'age_min' in search_data and 'age_max' in search_data:
        if search_data['age_min'] > search_data['age_max']:
            return False, "'age_min' cannot be greater than 'age_max'"
    
    # Validate fame rating (new format)
    if 'fame_rating' in search_data:
        fame_rating = search_data['fame_rating']
        if not isinstance(fame_rating, dict):
            return False, "'fame_rating' must be a dictionary"
        
        if 'min' in fame_rating:
            if not isinstance(fame_rating['min'], (int, float)) or fame_rating['min'] < 0:
                return False, "'fame_rating.min' must be a number >= 0"
        
        if 'max' in fame_rating:
            if not isinstance(fame_rating['max'], (int, float)) or fame_rating['max'] > 100:
                return False, "'fame_rating.max' must be a number <= 100"
        
        if 'min' in fame_rating and 'max' in fame_rating:
            if fame_rating['min'] > fame_rating['max']:
                return False, "'fame_rating.min' cannot be greater than 'fame_rating.max'"
    
    # Validate fame rating filters (legacy format)
    if 'fame_rating_min' in search_data:
        if not isinstance(search_data['fame_rating_min'], (int, float)) or search_data['fame_rating_min'] < 0:
            return False, "'fame_rating_min' must be a number >= 0"
    
    if 'fame_rating_max' in search_data:
        if not isinstance(search_data['fame_rating_max'], (int, float)) or search_data['fame_rating_max'] > 100:
            return False, "'fame_rating_max' must be a number <= 100"
    
    if 'fame_rating_min' in search_data and 'fame_rating_max' in search_data:
        if search_data['fame_rating_min'] > search_data['fame_rating_max']:
            return False, "'fame_rating_min' cannot be greater than 'fame_rating_max'"
    
    # Validate coordinates (new format - GPS-based search with radius)
    if 'coordinates' in search_data:
        coordinates = search_data['coordinates']
        
        if not isinstance(coordinates, dict):
            return False, "'coordinates' must be a dictionary"
        
        # latitude and longitude are required for coordinates search
        if 'latitude' not in coordinates or 'longitude' not in coordinates:
            return False, "'coordinates' must include 'latitude' and 'longitude'"
        
        if not isinstance(coordinates['latitude'], (int, float)) or not (-90 <= coordinates['latitude'] <= 90):
            return False, "'coordinates.latitude' must be a number between -90 and 90"
        
        if not isinstance(coordinates['longitude'], (int, float)) or not (-180 <= coordinates['longitude'] <= 180):
            return False, "'coordinates.longitude' must be a number between -180 and 180"
        
        # distance/radius is optional, defaults to 100km
        if 'distance' in coordinates:
            if not isinstance(coordinates['distance'], (int, float)) or coordinates['distance'] <= 0:
                return False, "'coordinates.distance' must be a positive number"
    
    # Validate location filter (new format - city/country based)
    if 'location' in search_data:
        location = search_data['location']
        
        if not isinstance(location, dict):
            return False, "'location' must be a dictionary"
        
        # For new format, city and country are optional (can use either or both)
        if 'city' in location:
            if not isinstance(location['city'], str) or not location['city'].strip():
                return False, "'location.city' must be a non-empty string"
        
        if 'country' in location:
            if not isinstance(location['country'], str) or not location['country'].strip():
                return False, "'location.country' must be a non-empty string"
        
        # Legacy format support: if latitude/longitude/radius are present, validate them
        if 'latitude' in location and 'longitude' in location:
            if not isinstance(location['latitude'], (int, float)) or not (-90 <= location['latitude'] <= 90):
                return False, "'location.latitude' must be a number between -90 and 90"
            
            if not isinstance(location['longitude'], (int, float)) or not (-180 <= location['longitude'] <= 180):
                return False, "'location.longitude' must be a number between -180 and 180"
            
            if 'radius' in location:
                if not isinstance(location['radius'], (int, float)) or location['radius'] <= 0:
                    return False, "'location.radius' must be a positive number"
    
    # Validate interests (new format)
    if 'interests' in search_data:
        if not isinstance(search_data['interests'], list):
            return False, "'interests' must be a list"
        
        if not all(isinstance(tag, str) and tag.strip() for tag in search_data['interests']):
            return False, "'interests' must be a list of non-empty strings"
    
    # Validate interests match mode
    if 'interests_match_mode' in search_data:
        if search_data['interests_match_mode'] not in ['OR', 'AND']:
            return False, "'interests_match_mode' must be either 'OR' or 'AND'"
    
    # Validate tags filter (legacy format)
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
    
    # Validate sort_by
    if 'sort_by' in search_data:
        valid_sort_options = ['age', 'fame_rating', 'distance', 'interests', 'city', 'country', 'match_score', 'common_tags']
        if search_data['sort_by'] not in valid_sort_options:
            return False, f"'sort_by' must be one of: {', '.join(valid_sort_options)}"
    
    # Validate sort_order
    if 'sort_order' in search_data:
        if search_data['sort_order'] not in ['asc', 'desc']:
            return False, "'sort_order' must be either 'asc' or 'desc'"
    
    return True, "Valid search data"
