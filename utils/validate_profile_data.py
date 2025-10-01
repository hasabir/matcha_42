
import logging

logger = logging.getLogger(__name__)


def validate_profile_data(request_data):
    """Validate profile creation data with detailed error messages"""
    
    logger.debug(f"⚠️⚠️⚠️ request data -> {request_data} ⚠️⚠️⚠️")
    # Define required fields with validation rules
    required_fields = {
        'bio': {'min_length': 0, 'max_length': 500},
        'gender': {'allowed_values': ['Male', 'Female', 'Non-binary', 'Other']},
        'age': {'min_value': 18, 'max_value': 120},
        # 'location': {'min_length': 2, 'max_length': 100},
        # 'profile_picture': {'type': 'text'}, 
        'sexual_preferences': {'allowed_values': ['Men', 'Women', 'Both', 'All']}
    }
    
    
    # errors = "there is no error for the moment"
    errors = []
    # Check for missing fields
    missing_fields = [field for field in required_fields if field not in request_data or not request_data[field]]
    if missing_fields:
        errors.append(f"Missing required fields: {', '.join(missing_fields)}")
    
    # Validate each field that is present
    for field, rules in required_fields.items():
        if field not in request_data:
            continue
            
        value = request_data[field]
        
        # Check if field is empty
        if field != "bio" and not value:
            errors.append(f"{field} cannot be empty")
            continue
            
        # Validate based on field type
        if field == 'age':
            try:
                num_value = int(value)
                if 'min_value' in rules and num_value < rules['min_value']:
                    errors.append(f"{field} must be at least {rules['min_value']}")
                if 'max_value' in rules and num_value > rules['max_value']:
                    errors.append(f"{field} cannot exceed {rules['max_value']}")
            except (ValueError, TypeError):
                errors.append(f"{field} must be a valid number")
                
        elif field == 'bio' or field == 'location':
            if 'min_length' in rules and len(value) < rules['min_length']:
                errors.append(f"{field} must be at least {rules['min_length']} characters")
            if 'max_length' in rules and len(value) > rules['max_length']:
                errors.append(f"{field} cannot exceed {rules['max_length']} characters")
                
        elif field == 'gender' or field == 'sexual_preferences':
            if 'allowed_values' in rules and value not in rules['allowed_values']:
                errors.append(f"{field} must be one of: {', '.join(rules['allowed_values'])}")
                
        # elif field == 'profile_picture':
        #     # Simple URL validation
        #     if 'type' in rules and rules['type'] == 'url':
        #         if not value.startswith(('http://', 'https://')):
        #             errors.append("profile_picture must be a valid URL")
    
    return errors