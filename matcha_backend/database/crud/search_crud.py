from database.crud.location_crud import Location
from ..dbmanager import DBManager
from psycopg2 import sql

import logging
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)



from ..dbmanager import DBManager
from psycopg2 import sql
import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Search(DBManager):
    def __init__(self, connection_pool, filter=False):
        super().__init__(connection_pool)
        self.filter = filter
        self.connection_pool = connection_pool
        
    def search_users(self, criteria, usernames_list=None):
        """Search users based on criteria and return only usernames."""
        age_range = criteria.get('age_range', {})
        location = criteria.get('location', {})
        coordinates = criteria.get('coordinates', {})
        distance = criteria.get('distance', 10)
        interests = criteria.get('interests', [])
        fame_rating = criteria.get('fame_rating', {})

        
        query_parts = [
            sql.SQL("SELECT DISTINCT u.username FROM users u"),
            sql.SQL("INNER JOIN profiles p ON u.id = p.user_id")
        ]
        
        params = []
        conditions = [
            sql.SQL("u.verified = TRUE"),
            # sql.SQL("u.active = TRUE")
        ]
        
        # Handle filter mode with usernames list
        if self.filter:
            if not usernames_list:
                raise ValueError("Usernames list must be provided in filter mode.")
            placeholders = sql.SQL(',').join([sql.Placeholder()] * len(usernames_list))
            conditions.append(sql.SQL("u.username IN ({})").format(placeholders))
            params.extend(usernames_list)  # Add usernames to params FIRST
        
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
            # logger.debug(f"✅✅✅✅Age Range: {age_range}")
            conditions.append(sql.SQL("p.age >= %s AND p.age <= %s"))
            # logger.debug(f"✅✅✅✅Conditions: {conditions}")
            params.extend([age_range['min_age'], age_range['max_age']])
        # if 'min_age' in age_range and 'max_age' in age_range:
        #     conditions.append(sql.SQL("p.age BETWEEN %s AND %s"))
        #     params.extend([age_range['min_age'], age_range['max_age']])
        
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
        
        # Interests condition
        if interests:
            conditions.append(sql.SQL("t.tag_name = ANY(%s)"))
            params.append(interests)
        
        # Build the final query
        base_query = sql.SQL(' ').join(query_parts)
        
        if conditions:
            where_clause = sql.SQL(' AND ').join(conditions)
            final_query = sql.SQL('{base} WHERE {where}').format(
                base=base_query,
                where=where_clause
            )
        else:
            final_query = base_query
        
        # Execute the query
        # logger.info(f"Final Query: {final_query.as_string(self.conn)}")
        # logger.info(f"Parameters: {params}")
        logger.debug(f"Final Query: {final_query}")
        result = self.execute(final_query, tuple(params))
        return [row['username'] for row in result]
    
    def filter_users(self, usernames_list, criteria):
        """Filter users based on criteria and return only usernames."""
        # Set filter mode and call search_users
        self.filter = True
        return self.search_users(criteria, usernames_list)
    
    
    
    def sort_users(self, request_data, user_id):
        """Sort users based on a specified attribute and return only usernames."""
        # Fix 1: Correct the validation logic (use OR instead of AND)
        if "sort_by" not in request_data or request_data["sort_by"] not in ['age', 'fame_rating', 'interests', 'location']:
            raise ValueError("Invalid sort_by value. Must be 'age', 'fame_rating', 'interests', or 'location'.")
        
        # Fix 2: Correct the order validation logic
        if "order" not in request_data or request_data["order"] not in ['asc', 'desc']:
            raise ValueError("Invalid order value. Must be 'asc' or 'desc'.")
        
        sort_by = request_data["sort_by"]
        order = request_data["order"]
        usernames_list = request_data["usernames"]
        max_distance_km = request_data.get("max_distance_km", 100) if sort_by == "location" else None
        
        # Fix 3: Handle location sorting separately since it doesn't use SQL query
        if sort_by == 'location':
            location_crud = Location(self.connection_pool)
            sorted_users = location_crud.find_nearby_users(user_id, max_distance_km)
            return sorted_users
        
        # Fix 4: Initialize params variable
        params = ()
        
        # Fix 5: Handle age and fame_rating sorting
        if sort_by == 'age' or sort_by == 'fame_rating':
            placeholders = sql.SQL(',').join([sql.Placeholder()] * len(usernames_list))
            query = sql.SQL("""
                SELECT u.username FROM users u
                INNER JOIN profiles p ON u.id = p.user_id
                WHERE u.username IN ({usernames})
                ORDER BY {sort_by} {order}
            """).format(
                usernames=placeholders,
                sort_by=sql.Identifier(sort_by),
                order=sql.SQL(order.upper())
            )
            params = tuple(usernames_list)
        
        # Fix 6: Handle interests sorting
        elif sort_by == 'interests':
            tags = request_data.get("tags", [])
            if not tags:
                raise ValueError("Tags must be provided when sorting by interests.")
            
            placeholders = sql.SQL(',').join([sql.Placeholder()] * len(usernames_list))
            tag_placeholders = sql.SQL(',').join([sql.Placeholder()] * len(tags))
            
            query = sql.SQL("""
                SELECT 
                    u.username, 
                    COUNT(CASE WHEN t.tag_name IN ({search_tags}) THEN 1 ELSE NULL END) as matching_interest_count 
                FROM users u
                INNER JOIN user_tags ut ON u.id = ut.user_id
                INNER JOIN tags t ON ut.tag_id = t.tag_id
                WHERE u.username IN ({usernames})
                GROUP BY u.username
                ORDER BY matching_interest_count {order}
            """).format(
                usernames=placeholders,
                search_tags=tag_placeholders,
                order=sql.SQL(order.upper())
            )
            
            # Include both usernames AND tags in parameters
            params = tuple(usernames_list + tags)
            
        logger.debug(f"⚠️⚠️query: {query}")
        
        # Fix 7: Execute query and return results
        result = self.execute(query, params)
        logger.debug(f"⚠️⚠️✅ ❌result: {result}")
        if not result:
            return []
        sorted_users = [row['username'] for row in result]
        return sorted_users