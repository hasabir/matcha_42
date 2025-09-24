from ..dbmanager import DBManager
import logging
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

        
        # SELECT DISTINCT u.username
        # FROM users u
        # INNER JOIN profiles p ON u.id = p.user_id
        # INNER JOIN user_locations ul ON u.id = ul.user_id
        # INNER JOIN user_tags ut ON u.id = ut.user_id
        # INNER JOIN tags t ON ut.tag_id = t.tag_id
        # WHERE p.age BETWEEN 18 AND 25
        #     AND ul.city = 'New York'
        #     AND ul.country = 'USA'
        #     AND p.gender = 'female'
        #     AND p.fame_rating BETWEEN 0 AND 100
        #     AND t.tag_name = 'web'
        #     AND u.verified = TRUE  -- Assuming you want verified users
        #     AND u.active = TRUE;   -- And active users


# class Search(DBManager):
#     def __init__(self, connection_pool):
#         super().__init__(connection_pool)
        
#     def search_users(self, criteria):
#         """Search users based on criteria like age range, location, interests, and fame rating."""
#         # This is a placeholder implementation. Actual implementation would involve complex SQL queries.
#         logger.info(f"Searching users with criteria: {criteria}")
#         # Example criteria processing (to be replaced with actual logic)
        
        
#         age_range = criteria.get('age_range', {})
#         location = criteria.get('location', {})
#         coordinates = criteria.get('coordinates', {})
#         distance = criteria.get('distance', 10)  # default distance in km
#         interests = criteria.get('interests', [])
#         fame_rating = criteria.get('fame_rating', 0)
        
        
#         # Build SQL query based on criteria
#         query = "SELECT DISTINCT u.username FROM users u "
#         query += "INNER JOIN profiles p ON u.id = p.user_id "
#         if location or coordinates:
#             query += "INNER JOIN user_locations ul ON u.id = ul.user_id "
#         if interests:
#             query += "INNER JOIN user_tags ut ON u.id = ut.user_id "
#             query += "INNER JOIN tags t ON ut.tag_id = t.tag_id "
#         query += "WHERE u.verified = TRUE AND u.active = TRUE "
#         params = []
#         if 'min_age' in age_range and 'max_age' in age_range:
#             query += "AND p.age BETWEEN %s AND %s "
#             params.extend([age_range['min_age'], age_range['max_age']])
#         if coordinates:
#             if 'latitude' in coordinates and 'longitude' in coordinates:
#                 # Haversine formula to calculate distance
#                 query += ("AND (6371 * acos(cos(radians(%s)) * cos(radians(ul.latitude)) * "
#                           "cos(radians(ul.longitude) - radians(%s)) + "
#                           "sin(radians(%s)) * sin(radians(ul.latitude)))) <= %s ")
#                 params.extend([coordinates['latitude'], coordinates['longitude'],
#                                coordinates['latitude'], distance])
#         elif location:
#             if 'city' in location and 'country' in location:
#                 query += "AND ul.city = %s AND ul.country = %s "
#                 params.extend([location['city'], location['country']])
#         if fame_rating:
#             query += "AND p.fame_rating BETWEEN %s AND %s "
#             params.extend([0, fame_rating])
#         if interests:
#             query += "AND t.tag_name = ANY(%s) "
#             params.append(interests)
#         self.execute(query, tuple(params))
#         results = [row['username'] for row in self.cursor.fetchall()]
#         return results




class Search(DBManager):
    def __init__(self, connection_pool):
        super().__init__(connection_pool)
        
    def search_users(self, criteria):
        """Search users based on criteria and return only usernames."""
        age_range = criteria.get('age_range', {})
        location = criteria.get('location', {})
        coordinates = criteria.get('coordinates', {})
        distance = criteria.get('distance', 10)
        interests = criteria.get('interests', [])
        fame_rating = criteria.get('fame_rating', {})
        
        query = "SELECT DISTINCT u.username FROM users u "
        query += "INNER JOIN profiles p ON u.id = p.user_id "
        
        params = []
        
        if location or coordinates:
            query += "INNER JOIN user_locations ul ON u.id = ul.user_id "
        if interests:
            query += "INNER JOIN user_tags ut ON u.id = ut.user_id "
            query += "INNER JOIN tags t ON ut.tag_id = t.tag_id "
        
        query += "WHERE u.verified = TRUE AND u.active = TRUE "
        
        if 'min_age' in age_range and 'max_age' in age_range:
            query += "AND p.age BETWEEN %s AND %s "
            params.extend([age_range['min_age'], age_range['max_age']])
        
        if coordinates and 'latitude' in coordinates and 'longitude' in coordinates:
            query += """
                AND (6371 * acos(cos(radians(%s)) * cos(radians(ul.latitude)) * 
                cos(radians(ul.longitude) - radians(%s)) + 
                sin(radians(%s)) * sin(radians(ul.latitude)))) <= %s 
            """
            params.extend([coordinates['latitude'], coordinates['longitude'],
                         coordinates['latitude'], distance])
        elif location:
            if 'city' in location and location['city']:
                query += "AND ul.city = %s "
                params.append(location['city'])
            if 'country' in location and location['country']:
                query += "AND ul.country = %s "
                params.append(location['country'])
        
        if 'min' in fame_rating and 'max' in fame_rating:
            query += "AND p.fame_rating BETWEEN %s AND %s "
            params.extend([fame_rating['min'], fame_rating['max']])
        
        if criteria.get('gender'):
            query += "AND p.gender = %s "
            params.append(criteria['gender'])
        
        if interests:
            query += "AND t.tag_name = ANY(%s) "
            params.append(interests)
        
        query += "ORDER BY p.fame_rating DESC"
        
        self.execute(query, tuple(params))
        return [row['username'] for row in self.cursor.fetchall()]