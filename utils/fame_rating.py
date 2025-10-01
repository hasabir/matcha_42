def calculate_fame_rating(old_rating, type):
    allowed_types = ['like', 'dislike',
                     'visit', 'block',
                     'unblock', 'report']
    if type not in allowed_types:
        raise ValueError("Invalid type. Allowed types are: " + ", ".join(allowed_types))
    if type == 'like':
        return old_rating + 5
    elif type == 'dislike':
        return old_rating - 5
    elif type == 'visit':
        return old_rating + 1
    elif type == 'block':
        return old_rating - 13
    elif type == 'unblock':
        return old_rating + 13
    elif type == 'report':
        return old_rating - 21
    return old_rating
