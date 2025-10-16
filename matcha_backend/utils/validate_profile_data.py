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
        valid_genders = ['male', 'female', 'non-binary', 'other']
        if data['gender'].lower() not in valid_genders:
            raise ValueError(f"Gender must be one of: {', '.join(valid_genders)}")
    
    if 'sexual_preference' in data:
        valid_preferences = ['male', 'female', 'bisexual', 'all']
        if data['sexual_preference'].lower() not in valid_preferences:
            raise ValueError(f"Sexual preference must be one of: {', '.join(valid_preferences)}")
    
    if 'biography' in data and data['biography']:
        if len(data['biography']) > 500:
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
