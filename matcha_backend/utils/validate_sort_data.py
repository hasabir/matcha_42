
import logging
logger = logging.getLogger(__name__)

def validate_sort_data(sort_data):
    '''sort users based on criteria
    Expects a json body with sort criteria and list of usernames.
    Example: { "sort_by": "age" or "fame_rating" or "location" or "interests" or "city" or "country",
    "order": "asc" or "desc",
    "usernames": [user1, user2, user3] }'''
    sort_criteria = ['age', 'fame_rating', 'location', 'interests', 'city', 'country']
    if not sort_data:
        return False, "No data provided."
    if 'sort_by' not in sort_data:
        return False, "'sort_by' field is required."
    if sort_data.get('sort_by') not in sort_criteria:
        return False, f"Invalid 'sort_by' value. It must be one of: {', '.join(sort_criteria)}"

    if 'order' not in sort_data:
        return False, "'order' field is required."
    if sort_data.get('order') not in ['asc', 'desc']:
        return False, "'order' must be either 'asc' or 'desc'."
    if 'usernames' not in sort_data:
        return False, "'usernames' field is required."
    if (not isinstance(sort_data['usernames'], list) or
        not all(isinstance(username, str) and username.strip() for username in sort_data['usernames'])):
        return False, "'usernames' must be a list of non-empty strings."
    if len(sort_data['usernames']) == 0:
        return False, "'usernames' list cannot be empty."
    if not isinstance(sort_data["sort_by"], str):
        return False, "'sort_by' must be a string."
    if not isinstance(sort_data["order"], str):
        return False, "'order' must be a string."
    
    # Tags are now optional - if not provided, will use current user's tags
    if "tags" in sort_data:
        if not isinstance(sort_data["tags"], list):
            return False, "'tags' must be a list when provided."
        if not all(isinstance(tag, str) and tag.strip() for tag in sort_data["tags"]):
            return False, "'tags' must be a list of non-empty strings."
    
    return True, "Valid sort data."