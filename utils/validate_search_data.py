
def validate_search_data(data):
    expected_fields = ['age_range', 'interests',
                       'fame_rating', 'location',
                       'coordinates', 'distance']
    if filter:
        expected_fields.append('usernames')
    
    if not data:
        return False, "No data provided."
    
    incorrect_fields = [field for field in data if field not in expected_fields]
    # missing_fields = [field for field in expected_fields if field not in data]

    if incorrect_fields:
        return False, f"Unexpected fields: {', '.join(incorrect_fields)}. expected fields are: {expected_fields}"
    # if missing_fields:
    #     return False, f"Missing required fields: {', '.join(missing_fields)}"
    # if 'location' or 'coordinates' not in data:
    #     return False, "Either 'location with city name and country name' or 'coordinates' must be provided."
    
   
    if 'age_range' in data:
        age_range = data['age_range']
        if (not isinstance(age_range, dict) or len(age_range) != 2 or
            'min_age' not in age_range or 'max_age' not in age_range or
            not isinstance(age_range['min_age'], int) or
            not isinstance(age_range['max_age'], int) or
            not (18 <= age_range['min_age'] <= age_range['max_age'] <= 100)):
            return False, "Invalid age_range. It should be a dictionary with two keys: \
                'min_age' and 'max_age', both integers, \
                    where 18 <= min_age <= max_age <= 100."
    if 'coordinates' in data:
    
        location = data['coordinates']
        if (not isinstance(location, dict) or
            'latitude' not in location or 'longitude' not in location or
            not isinstance(location['latitude'], (int, float)) or
            not isinstance(location['longitude'], (int, float)) or
            not (-90 <= location['latitude'] <= 90) or
            not (-180 <= location['longitude'] <= 180)):
            return False, "Invalid location. It should be a dictionary with 'latitude' and 'longitude' keys having valid float values."
        
        if 'distance' not in data:
            return False, "If 'coordinates' is provided, 'distance' must also be provided."
        distance = data['distance']
        if not isinstance(distance, int) or distance < 0:
            return False, "Invalid distance. It should be a non-negative integer."

    elif 'location' in data:
        location = data['location']
        if not isinstance(location, dict) or len(location) != 2 or \
            'city' not in location or 'country' not in location or \
            not all(isinstance(location[key], str) and location[key].strip() for key in location):
            return False, "Invalid location. It should be a dictionary with 'city' and 'country' keys having non-empty string values."

    if 'fame_rating' in data:
        fame_rating = data['fame_rating']
        if not isinstance(fame_rating, dict) or 'max' not in fame_rating or \
           not isinstance(fame_rating['max'], int) or fame_rating['max'] < 0 or \
           ('min' in fame_rating and (not isinstance(fame_rating['min'], int) or \
               fame_rating['min'] < 0 or fame_rating['min'] > fame_rating['max'] )):
            return False, "Invalid fame_rating. It should be a non-negative integer."   
    
    
    if 'interests' in data:
        interests = data['interests']
        if not isinstance(interests, list) or not all(isinstance(interest, str) for interest in interests):
            return False, "Invalid interests. It should be a list of strings."
    

    return True, "Valid search data."
