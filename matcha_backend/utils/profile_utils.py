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
    
    # Construct profile picture URL
    profile_pic = profile_data.get("profile_picture")
    if profile_pic:
        # Fix old folder typo: pofile_picture -> profile_picture
        profile_pic = profile_pic.replace("/pofile_picture/", "/profile_picture").replace("pofile_picture/", "profile_picture/")
        
        # Remove any /static/ prefixes (we'll add it back properly)
        profile_pic = profile_pic.lstrip("/")
        if profile_pic.startswith("static/"):
            profile_pic = profile_pic[7:]  # Remove "static/"
        
        # Now add the full URL with /static/ prefix
        from flask import url_for, request
        # Get the backend base URL
        backend_url = request.host_url.rstrip("/")  # e.g., "http://localhost:5000"
        profile_pic = f"{backend_url}/static/{profile_pic}"
    
    result = {
        "id": user_data.get("id"),
        "user_id": user_data.get("id"),  # Alias for compatibility
        "first_name": user_data.get("first_name") or "",
        "last_name": user_data.get("last_name") or "",
        "username": user_data.get("username") or "",
        "location": Location(connection_pool).get_user_location(user_id),
        "tags": profile_crud.get_user_interests(user_id) or [],
        "images": profile_crud.get_images(user_id) or [],
        "bio": profile_data.get("bio") or "",
        "fame_rating": profile_data.get("fame_rating") or 0,
        "age": profile_data.get("age"),
        "sexual_preferences": profile_data.get("sexual_preferences") or "",
        "gender": profile_data.get("gender") or "",
        "profile_picture": profile_pic,
        "active": user_data.get("active", False),
        "last_seen": user_data.get("last_seen")
    }
    
    return result