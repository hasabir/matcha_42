"""
Profile data validation utilities
"""
import re
from datetime import datetime

def validate_profile_data(data, required_fields=None):
    """
    Validate profile data
    
    Args:
        data: Dictionary containing profile data to validate
        required_fields: List of required field names (optional)
    
    Returns:
        tuple: (is_valid, error_message)
    
    Raises:
        ValueError: If validation fails
    """
    if not data:
        raise ValueError("No data provided")
    
    # Normalize keys and values (accept multiple aliases from frontend)
    aliases = {
        'biography': 'bio',
        'sexual_preference': 'sexual_preferences',
        'sexualPreference': 'sexual_preferences',
        'sex_pref': 'sexual_preferences',
    }
    normalized = {}
    for k, v in (data or {}).items():
        key = aliases.get(k, k)
        # Strip spaces and normalize string values
        if isinstance(v, str):
            v = v.strip()
        normalized[key] = v

    # Map human-friendly values to canonical ones
    # Gender: normalize to lowercase (male, female, other)
    if 'gender' in normalized and isinstance(normalized['gender'], str):
        gender_map = {
            'male': 'male',
            'female': 'female',
            'non-binary': 'other',
            'nonbinary': 'other',
            'other': 'other',
            # Legacy capitalized values
            'Male': 'male',
            'Female': 'female',
            'Non-binary': 'other',
            'Other': 'other'
        }
        normalized['gender'] = gender_map.get(normalized['gender'], normalized['gender'].lower())

    # Sexual preferences: normalize to male/female/both
    # The matching algorithm expects: 'male', 'female', or 'both'
    # DEFAULT: If not specified, default to 'both' (bisexual behavior)
    if 'sexual_preferences' in normalized and normalized['sexual_preferences']:
        if isinstance(normalized['sexual_preferences'], str):
            pref_map = {
                # Target: 'male' (for users looking for men)
                'men': 'male',
                'man': 'male',
                'male': 'male',
                'Male': 'male',
                'Men': 'male',
                # Target: 'female' (for users looking for women)
                'women': 'female',
                'woman': 'female',
                'female': 'female',
                'Female': 'female',
                'Women': 'female',
                # Target: 'both' (for bisexual/pansexual users)
                'both': 'both',
                'Both': 'both',
                'all': 'both',
                'All': 'both',
                'everyone': 'both',
                'Everyone': 'both',
                'bisexual': 'both',
                'Bisexual': 'both'
            }
            normalized['sexual_preferences'] = pref_map.get(normalized['sexual_preferences'], normalized['sexual_preferences'].lower())
    else:
        # Default to 'both' (bisexual) if not specified
        normalized['sexual_preferences'] = 'both'

    # From here on, use normalized dict
    # Update the original data dict in-place with normalized values
    data.clear()
    data.update(normalized)

    if required_fields:
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                raise ValueError(f"Required field '{field}' is missing or empty")
    
    # Validate specific fields if present
    if 'age' in data:
        try:
            age = int(data['age'])
            if age < 18 or age > 120:
                raise ValueError("Age must be between 18 and 120")
        except (ValueError, TypeError):
            raise ValueError("Invalid age format")
    
    if 'gender' in data:
        valid_genders = ['male', 'female', 'other']
        if data['gender'].lower() not in valid_genders:
            raise ValueError(f"Gender must be one of: {', '.join(valid_genders)}")
    
    if 'sexual_preferences' in data:
        valid_preferences = ['male', 'female', 'both']
        if data['sexual_preferences'].lower() not in valid_preferences:
            raise ValueError(f"Sexual preference must be one of: {', '.join(valid_preferences)}")
    
    # Support both 'bio' and 'biography'
    bio_text = data.get('bio') or data.get('biography')
    if bio_text:
        if len(bio_text) > 500:
            raise ValueError("Biography must not exceed 500 characters")
    
    if 'first_name' in data and data['first_name']:
        if len(data['first_name']) > 50:
            raise ValueError("First name must not exceed 50 characters")
        if not re.match(r'^[a-zA-Z\s\-\']+$', data['first_name']):
            raise ValueError("First name contains invalid characters")
    
    if 'last_name' in data and data['last_name']:
        if len(data['last_name']) > 50:
            raise ValueError("Last name must not exceed 50 characters")
        if not re.match(r'^[a-zA-Z\s\-\']+$', data['last_name']):
            raise ValueError("Last name contains invalid characters")
    
    return True
