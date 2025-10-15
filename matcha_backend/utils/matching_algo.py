import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))

from database.crud.location_crud import Location
from database.crud.user_crud import User
from database.crud.profile_crud import Profile
from database.crud.interactions_crud import Interactions
import logging
logger = logging.getLogger(__name__)
# Filter by sexual preferences
def filter_by_preferences(users, user_preferences):
    if user_preferences == 'both':
        return [user['user_id'] for user in users if user]
    filtered_usernames = []
    for user in users:
        if not user:
            continue
        if user_preferences == 'men' and user.get('gender') == 'male':
            filtered_usernames.append(user['user_id'])
        elif user_preferences == 'women' and user.get('gender') == 'female':
            filtered_usernames.append(user['user_id'])
    return filtered_usernames


# Calculate distance between users
def calculate_distance(connection_pool, user_id, filtered_usernames):
    try:
        location_crud = Location(connection_pool=connection_pool)
        nearby_users = location_crud.find_nearby_users(user_id, 50, usernames=filtered_usernames)
        return nearby_users
    except Exception as e:
        print(f"Error calculating distance: {e}")
        raise e


def calculate_match_score(user_data, candidate_data, nearby_users):
    '''
    Calculate match score between user and candidate
    
    Args:
        user_data: dict with keys 'username', 'user_tags' (set), 'fame_rating'
        candidate_data: dict with keys 'username', 'user_tags' (set), 'fame_rating'
        nearby_users: list of nearby usernames
    
    Returns:
        float: match score between 0 and 1
    '''
    
    weights = {
        'geography': 0.4,    # Highest priority
        'tags': 0.4,         # High priority  
        'fame': 0.2          # Lower priority
    }
    
    # Geography score (binary or scaled)
    geo_score = 1.0 if candidate_data['username'] in nearby_users else 0.0
    
    # Tags score (Jaccard similarity)
    user_tags = user_data["user_tags"] if isinstance(user_data["user_tags"], set) else set(user_data["user_tags"])
    candidate_tags = candidate_data["user_tags"] if isinstance(candidate_data["user_tags"], set) else set(candidate_data["user_tags"])
    
    common_tags = user_tags.intersection(candidate_tags)
    all_tags = user_tags.union(candidate_tags)
    tag_score = len(common_tags) / max(len(all_tags), 1)
    
    # Fame score (normalized)
    fame_score = candidate_data["fame_rating"] / 100
    
    # Weighted combination
    total_score = (
        geo_score * weights['geography'] +
        # tag_score * weights['tags'] + 
        fame_score * weights['fame']
    )
    
    return total_score


def matching_suggestions(connection_pool, user_id):
    # try:
        user_crud = User(connection_pool=connection_pool)
        profile_crud = Profile(connection_pool=connection_pool)
        
        # Get current user's profile
        user_profile = profile_crud.get_profile_by_user_id(user_id)
        if not user_profile:
            raise ValueError("User profile not found")
        
        # Get all users except current user
        users = user_crud.get_all_users()
        users = [user for user in users if user['id'] != user_id]
        
        # Get profiles for all users
        user_profiles = [profile_crud.get_profile_by_user_id(user['id']) for user in users]
        
        # Filter by sexual preferences
        filtered_ids = filter_by_preferences(user_profiles, user_profile["sexual_preferences"])
        
        # Exclude blocked users
        filtered_ids = [
            uid for uid in filtered_ids
            if not Interactions(connection_pool, user_id, uid).is_blocked()
        ]
        
        if not filtered_ids:
            return []
        
        # Get usernames for filtered users
        filtered_usernames = [
            user_crud.get_user_by('id', uid, 'username')['username'] 
            for uid in filtered_ids
        ]
        
        # Calculate nearby users
        nearby_users = calculate_distance(connection_pool, user_id, filtered_usernames)
        nearby_usernames = [user['username'] for user in nearby_users] if nearby_users else []
        
        # Prepare current user data
        user_data = {
            "username": user_crud.get_user_by('id', user_id, 'username')['username'],
            
            "user_tags": set(profile_crud.get_user_interests(user_id=user_id)),
            "fame_rating": user_profile['fame_rating']
        }
        # logger.debug(f"📬📬📬📬📬📬 user_tags = {profile_crud.get_user_interests(user_id=user_id)}")
        
        # Build candidate profiles and calculate scores
        suggested_users = {}
        
        for uid in filtered_ids:
            profile_data = profile_crud.get_profile_by_user_id(uid)
            username = user_crud.get_user_by('id', uid, 'username')['username']
            user_tags = profile_crud.get_user_interests(uid)
            
            candidate_data = {
                "username": username,
                "user_tags": set(user_tags),
                "fame_rating": profile_data['fame_rating']
            }
            
            # Calculate match score
            score = calculate_match_score(user_data, candidate_data, nearby_usernames)
            suggested_users[username] = score
        
        # Sort suggested users by score (descending)
        sorted_suggestions = sorted(
            suggested_users.items(),
            key=lambda item: item[1],
            reverse=True
        )
        
        return sorted_suggestions
        
    # except Exception as e:
    #     raise e














# import os
# import sys
# sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))

# from database.crud.location_crud import Location
# from database.crud.user_crud import User
# from database.crud.profile_crud import Profile
# from database.crud.interactions_crud import Interactions

# # from utils.profile_utils import get_profile_data


# #exemple profile:
# # {
# #             "age": 27,
# #             "bio": "Musician and food lover 🎸🍕",
# #             "fame_rating": 18,
# #             "gender": "male",
# #             "profile_id": 5,
# #             "profile_picture": null,
# #             "sexual_preferences": "women",
# #             "user_id": 5
# #         },






# #     Filter by sexual preferences
# def filter_by_preferences(users, user_preferences):
#     if user_preferences == 'both':
#         return [user['user_id'] for user in users if user]
#     filtered_usernames = []
#     for user in users:
#         if not user:
#             continue
#         if user_preferences == 'men' and user.get('gender') == 'male':
#             filtered_usernames.append(user['user_id'])
#         elif user_preferences == 'women' and user.get('gender') == 'female':
#             filtered_usernames.append(user['user_id'])
#     return filtered_usernames


# #     Calculate distance between users
# def calculate_distance(connection_pool ,user_id, filtred_usernames):
#     try:
#         location_crud = Location(connection_pool=connection_pool)
#         nearby_users = location_crud.find_nearby_users(user_id, 50, usernames=filtred_usernames)
        
#         # return [nearby_user["username"] for nearby_user in nearby_users] if nearby_users else []
#         return nearby_users
#     except Exception as e:
#         print(f"Error calculating distance: {e}")
#         raise e


# # count commen interests
# # def count_common_interests(user_interests, other_user_interests):



# def calculate_match_score(user_data, condidate_data, nearby_users):
#     '''
#         example user data:
#         user_data{
#             username: 'test',
#             'user_tags': [tag1, tag2],
#             'fame_rating': 20
#         }
#     '''
    
#     weights = {
#         'geography': 0.4,    # Highest priority
#         'tags': 0.4,         # High priority  
#         'fame': 0.2          # Lower priority
#     }
    
#     # Geography score (binary or scaled)
#     geo_score = 1.0 if condidate_data['username'] in nearby_users else 0.0
    
#     # Tags score (Jaccard similarity)
#     common_tags = user_data["user_tags"].intersection(condidate_data["user_tags"])
#     tag_score = len(common_tags) / max(len(user_data["user_tags"].union(condidate_data["user_tags"])), 1)
    
#     # Fame score (normalized)
#     fame_score = condidate_data["fame_rating"] / 100
    
#     # Weighted combination
#     total_score = (
#         geo_score * weights['geography'] +
#         tag_score * weights['tags'] + 
#         fame_score * weights['fame']
#     )
    
#     return total_score

# def matching_suggestions(connction_pool, user_id):
#     try:
#         user_crud = User(connection_pool=connction_pool)
#         profile_crud = Profile(connection_pool=connction_pool)
#         user_profile = profile_crud.get_profile_by_user_id(user_id)
#         if not user_profile:
#             raise ValueError("User profile not found")
#         users = user_crud.get_all_users()
#         # remove the current user from the list
#         users = [user for user in users if user['id'] != user_id]
#         user_profiles = [profile_crud.get_profile_by_user_id(user['id']) for user in users]
#         filtered_ids = filter_by_preferences(user_profiles, user_profile["sexual_preferences"])
#         # Exclude blocked users
#         filtered_ids = [
#             id for id in filtered_ids
#             if not Interactions(connction_pool, user_id, id).is_blocked()
#         ]
        
        
        
#         filtered_usernames = [user_crud.get_user_by('id', user_id, 'username')['username'] for user_id in filtered_ids]
        
#         filterd_profiles = []
        
#         for id in filtered_ids:
#             # get user profile from user_profiles list
#             filterd_profile = {}
#             profile_data = profile_crud.get_profile_by_user_id(id)
#             filterd_profile["username"] = user_crud.get_user_by('id', id, 'username')['username']
#             filterd_profile["user_tags"] = profile_crud.get_user_interests(id)
#             filterd_profile["fame_rating"] = profile_crud.get_profile_by_user_id(id)['fame_rating']
#             filterd_profiles.append(profile_data)
#         nearby_users = calculate_distance(connction_pool, user_id, filtered_usernames)
        
#         if not nearby_users:
#             return []
#         user_data = {}
#         user_data["username"] = user_crud.get_user_by('id', user_id, 'username')['username']
#         user_data["interests"] = profile_crud.get_user_interests(user_id=user_id)
#         user_data["fame_rating"] = profile_crud.get_profile_by_user_id(id)['fame_rating']
        
#         suggested_users = {}
#         for condidate_data in filterd_profiles:
#             suggested_users["username"] = calculate_match_score(user_data, condidate_data, nearby_users)
            
#         #sort suggested users based on the scor
#         sorted_suggestions = sorted(
#             suggested_users.items(),
#             key=lambda item: item[1],
#             reverse=True
#         )
        
#         return sorted_suggestions
#     except Exception as e:
#         raise e

    
    
