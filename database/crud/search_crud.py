from ..dbmanager import DBManager
from psycopg2 import sql

import logging
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)






from psycopg2 import sql

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
        
        # Start building query parts
        query_parts = [
            sql.SQL("SELECT DISTINCT u.username FROM users u"),
            sql.SQL("INNER JOIN profiles p ON u.id = p.user_id")
        ]
        
        params = []
        conditions = [
            sql.SQL("u.verified = TRUE"),
            sql.SQL("u.active = TRUE")
        ]
        
        # Add joins conditionally
        if location or coordinates:
            query_parts.append(sql.SQL("INNER JOIN user_locations ul ON u.id = ul.user_id"))
        
        if interests:
            query_parts.extend([
                sql.SQL("INNER JOIN user_tags ut ON u.id = ut.user_id"),
                sql.SQL("INNER JOIN tags t ON ut.tag_id = t.tag_id")
            ])
        
        # Age range condition
        if 'min_age' in age_range and 'max_age' in age_range:
            conditions.append(sql.SQL("p.age BETWEEN %s AND %s"))
            params.extend([age_range['min_age'], age_range['max_age']])
        
        # Location conditions
        if coordinates and 'latitude' in coordinates and 'longitude' in coordinates:
            conditions.append(sql.SQL("""
                (6371 * acos(cos(radians(%s)) * cos(radians(ul.latitude)) * 
                cos(radians(ul.longitude) - radians(%s)) + 
                sin(radians(%s)) * sin(radians(ul.latitude)))) <= %s
            """))
            params.extend([
                coordinates['latitude'], 
                coordinates['longitude'],
                coordinates['latitude'], 
                distance
            ])
        elif location:
            if 'city' in location and location['city']:
                conditions.append(sql.SQL("ul.city = %s"))
                params.append(location['city'])
            if 'country' in location and location['country']:
                conditions.append(sql.SQL("ul.country = %s"))
                params.append(location['country'])
        
        # Fame rating condition
        if 'min' in fame_rating and 'max' in fame_rating:
            conditions.append(sql.SQL("p.fame_rating BETWEEN %s AND %s"))
            params.extend([fame_rating['min'], fame_rating['max']])
        
        # # Gender condition
        # if criteria.get('gender'):
        #     conditions.append(sql.SQL("p.gender = %s"))
        #     params.append(criteria['gender'])
        
        # Interests condition
        if interests:
            conditions.append(sql.SQL("t.tag_name = ANY(%s)"))
            params.append(interests)
        
        # Build the final query
        base_query = sql.SQL(' ').join(query_parts)
        where_clause = sql.SQL(' AND ').join(conditions)
        final_query = sql.SQL('{base} WHERE {where}').format(
            base=base_query,
            where=where_clause
        )
        
        # Execute the query
        result = self.execute(final_query, tuple(params))
        return [row['username'] for row in result]


