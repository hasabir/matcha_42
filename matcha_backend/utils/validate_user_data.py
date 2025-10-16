def validate_user_data(user_data):
    required_fields = ["username", "email", "password", "first_name", "last_name"]
    for field in required_fields:
        if field not in user_data or not user_data[field]:
            return False
    return True