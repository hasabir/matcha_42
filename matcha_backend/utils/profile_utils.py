def houres_between_dates(start_date, end_date=None):
    if end_date is None:
        from datetime import datetime, timezone
        end_date = datetime.now(timezone.utc)
    delta = end_date.timestamp() - start_date.timestamp()
    return delta / 3600


def get_profile_data(connection_pool, user_id):
    from database.crud.user_crud import User
    from database.crud.profile_crud import Profile
    from database.crud.location_crud import Location
    user_crud = User(connection_pool)
    user_data = user_crud.get_user_by('id', user_id)
    if not user_data:
        return None
    profile_crud = Profile(connection_pool)
    profile_data = profile_crud.get_profile_by_user_id(user_id)
    if not profile_data:
        return None
    
    # Get location data
    location_data = Location(connection_pool).get_user_location(user_id)
    
    result = {
        "first_name": user_data["first_name"],
        "last_name": user_data["last_name"],
        "username": user_data["username"],
        "location": location_data,
        "city": location_data.get("city") if location_data else None,
        "country": location_data.get("country") if location_data else None,
        "tags": profile_crud.get_user_interests(user_id),
        "images": profile_crud.get_images(user_id),
        "profile_picture": profile_data.get("profile_picture"),
        "bio": profile_data["bio"],
        "fame_rating": profile_data["fame_rating"],
        "age": profile_data["age"],
        "birthdate": profile_data.get("birthdate"),
        "sexual_preferences": profile_data["sexual_preferences"],
        "gender": profile_data["gender"]
    }
    
    return result