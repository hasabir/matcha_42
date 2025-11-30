from ..dbmanager import DBManager
import logging
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
from utils.security import SecurityUtils
logging.basicConfig(level=logging.INFO)
from psycopg2 import sql


logger = logging.getLogger(__name__)



class Location(DBManager):
    def __init__(self, connection_pool):
        super().__init__(connection_pool)
        
        

    def set_user_location(self, user_id, latitude, longitude, city=None, country=None, neighborhood=None, accuracy=None):
        """Insert or update user location with proper UPSERT handling (includes neighborhood-level GPS positioning)"""
        location_data = {
            "user_id": user_id,
            "latitude": latitude,
            "longitude": longitude,
            "city": city,
            "country": country,
            "neighborhood": neighborhood,  # Neighborhood-level GPS positioning as per subject requirements
            "accuracy": accuracy
        }
        
        # Use ON CONFLICT to handle upsert - DBManager.insert() will handle the UPDATE automatically
        # when on_conflict='update' is specified
        return self.insert(
            table='user_locations',
            data=location_data,
            on_conflict='update',
            conflict_target=['user_id']
        )


    
    def get_user_location(self, user_id):
        """Retrieve user location by user ID (includes neighborhood-level data)"""
        result = self.select('user_locations', where="user_id = %s", where_params=(user_id,))
        location = {}
        if result:
            location = {
                "latitude": result[0]["latitude"],
                "longitude": result[0]["longitude"],
                "city": result[0]["city"],
                "country": result[0]["country"],
                "neighborhood": result[0].get("neighborhood"),  # Neighborhood-level GPS positioning
                "accuracy": result[0]["accuracy"]
            }
        return location
    
    def get_location_coordinates(self, user_id):
        """Retrieve only latitude and longitude for a user"""
        result = self.select('user_locations', columns=['latitude', 'longitude'], where="user_id = %s", where_params=(user_id,))
        if result:
            return {
                "latitude": result[0]["latitude"],
                "longitude": result[0]["longitude"]
            }
        return None
    
    
    def calculate_distance(self, user_id_1, user_id_2):
        """
        Calculate distance in kilometers between two users
        
        Args:
            user_id_1: ID of the first user
            user_id_2: ID of the second user
            
        Returns:
            Dictionary with distance_km or None if either user has no location
        """
        query = sql.SQL("""
            SELECT 
                ROUND(
                    CAST(
                        ST_Distance(
                            ST_SetSRID(ST_MakePoint(ul1.longitude, ul1.latitude), 4326)::geography,
                            ST_SetSRID(ST_MakePoint(ul2.longitude, ul2.latitude), 4326)::geography
                        ) / 1000 AS numeric
                    ), 1
                ) AS distance_km
            FROM user_locations ul1
            JOIN user_locations ul2 ON ul2.user_id = %s
            WHERE ul1.user_id = %s
            AND ul1.latitude IS NOT NULL 
            AND ul1.longitude IS NOT NULL
            AND ul2.latitude IS NOT NULL 
            AND ul2.longitude IS NOT NULL
        """)
        
        logger.debug(f"Calculating distance between user {user_id_1} and user {user_id_2}")
        result = self.execute(query, (user_id_2, user_id_1), fetch=True)
        logger.debug(f"Distance query result: {result}")
        if result and len(result) > 0:
            return result[0]
        return None
    
    def find_nearby_users(self, user_id, max_distance_km=100, usernames=None):
        """
        Find users near a given user within a specified distance
        
        Args:
            user_id: ID of the user to find neighbors for
            max_distance_km: Maximum distance in kilometers (default: 100km)
            usernames: Optional list of usernames to filter by
            
        Returns:
            List of nearby users with their distance in km
        """
        max_distance_meters = max_distance_km * 1000
        
        # Base query without username filtering
        base_query = sql.SQL("""
            SELECT 
                u.id,
                u.username,
                ROUND(
                    CAST(
                        ST_Distance(
                            ST_SetSRID(ST_MakePoint(ul1.longitude, ul1.latitude), 4326)::geography,
                            ST_SetSRID(ST_MakePoint(ul2.longitude, ul2.latitude), 4326)::geography
                        ) / 1000 AS numeric
                    ), 1
                ) AS distance_km
            FROM user_locations ul1
            JOIN user_locations ul2 ON ul2.user_id != ul1.user_id
            JOIN users u ON u.id = ul2.user_id
            WHERE ul1.user_id = %s
            AND ST_DWithin(
                ST_SetSRID(ST_MakePoint(ul1.longitude, ul1.latitude), 4326)::geography,
                ST_SetSRID(ST_MakePoint(ul2.longitude, ul2.latitude), 4326)::geography,
                %s
            )
        """)
        
        if usernames:
            # Apply username filter BEFORE distance calculation for better performance
            placeholders = sql.SQL(',').join([sql.Placeholder()] * len(usernames))
            query = sql.SQL("""
                {base_query}
                AND u.username IN ({usernames})
                ORDER BY distance_km ASC
            """).format(
                base_query=base_query,
                usernames=placeholders
            )
            params = (user_id, max_distance_meters, *usernames)
        else:
            query = sql.SQL("""
                {base_query}
                ORDER BY distance_km ASC
            """).format(base_query=base_query)
            params = (user_id, max_distance_meters)
        
        return self.execute(query, params)
    
    def get_location_by_user_id(self, user_id):
        """Get location record for a user (wrapper for compatibility)"""
        result = self.select('user_locations', where="user_id = %s", where_params=(user_id,))
        return result[0] if result else None
    
    def create_location(self, location_data):
        """Create a new location record (wrapper for set_user_location)"""
        return self.set_user_location(
            user_id=location_data['user_id'],
            latitude=location_data['latitude'],
            longitude=location_data['longitude'],
            city=location_data.get('city'),
            country=location_data.get('country'),
            neighborhood=location_data.get('neighborhood'),
            accuracy=location_data.get('accuracy')
        )
    
    def update_location(self, user_id, location_data):
        """Update an existing location record (wrapper for set_user_location)"""
        return self.set_user_location(
            user_id=user_id,
            latitude=location_data['latitude'],
            longitude=location_data['longitude'],
            city=location_data.get('city'),
            country=location_data.get('country'),
            neighborhood=location_data.get('neighborhood'),
            accuracy=location_data.get('accuracy')
        )
    
    def find_users_by_city(self, city, usernames=None):
        """
        Find users in a specific city
        
        Args:
            city: City name to search for (case-insensitive)
            usernames: Optional list of usernames to filter by
            
        Returns:
            List of users in the specified city
        """
        if usernames:
            placeholders = sql.SQL(',').join([sql.Placeholder()] * len(usernames))
            query = sql.SQL("""
                SELECT u.id, u.username, ul.city, ul.country
                FROM user_locations ul
                JOIN users u ON u.id = ul.user_id
                WHERE LOWER(ul.city) = LOWER(%s)
                AND u.username IN ({usernames})
                ORDER BY u.username ASC
            """).format(usernames=placeholders)
            params = (city, *usernames)
        else:
            query = sql.SQL("""
                SELECT u.id, u.username, ul.city, ul.country
                FROM user_locations ul
                JOIN users u ON u.id = ul.user_id
                WHERE LOWER(ul.city) = LOWER(%s)
                ORDER BY u.username ASC
            """)
            params = (city,)
        
        return self.execute(query, params)
    
    def find_users_by_country(self, country, usernames=None):
        """
        Find users in a specific country
        
        Args:
            country: Country name to search for (case-insensitive)
            usernames: Optional list of usernames to filter by
            
        Returns:
            List of users in the specified country
        """
        if usernames:
            placeholders = sql.SQL(',').join([sql.Placeholder()] * len(usernames))
            query = sql.SQL("""
                SELECT u.id, u.username, ul.city, ul.country
                FROM user_locations ul
                JOIN users u ON u.id = ul.user_id
                WHERE LOWER(ul.country) = LOWER(%s)
                AND u.username IN ({usernames})
                ORDER BY u.username ASC
            """).format(usernames=placeholders)
            params = (country, *usernames)
        else:
            query = sql.SQL("""
                SELECT u.id, u.username, ul.city, ul.country
                FROM user_locations ul
                JOIN users u ON u.id = ul.user_id
                WHERE LOWER(ul.country) = LOWER(%s)
                ORDER BY u.username ASC
            """)
            params = (country,)
        
        return self.execute(query, params)
    
    def sort_users_by_city(self, usernames, order='asc'):
        """
        Sort users alphabetically by city name
        
        Args:
            usernames: List of usernames to sort
            order: Sort order ('asc' or 'desc')
            
        Returns:
            List of usernames sorted by city
        """
        if not usernames:
            return []
        
        placeholders = sql.SQL(',').join([sql.Placeholder()] * len(usernames))
        order_clause = sql.SQL('ASC') if order.lower() == 'asc' else sql.SQL('DESC')
        
        query = sql.SQL("""
            SELECT u.username
            FROM users u
            LEFT JOIN user_locations ul ON u.id = ul.user_id
            WHERE u.username IN ({usernames})
            ORDER BY LOWER(COALESCE(ul.city, '')) {order}, u.username ASC
        """).format(
            usernames=placeholders,
            order=order_clause
        )
        
        result = self.execute(query, tuple(usernames))
        return [row['username'] for row in result] if result else []
    
    def sort_users_by_country(self, usernames, order='asc'):
        """
        Sort users alphabetically by country name
        
        Args:
            usernames: List of usernames to sort
            order: Sort order ('asc' or 'desc')
            
        Returns:
            List of usernames sorted by country
        """
        if not usernames:
            return []
        
        placeholders = sql.SQL(',').join([sql.Placeholder()] * len(usernames))
        order_clause = sql.SQL('ASC') if order.lower() == 'asc' else sql.SQL('DESC')
        
        query = sql.SQL("""
            SELECT u.username
            FROM users u
            LEFT JOIN user_locations ul ON u.id = ul.user_id
            WHERE u.username IN ({usernames})
            ORDER BY LOWER(COALESCE(ul.country, '')) {order}, u.username ASC
        """).format(
            usernames=placeholders,
            order=order_clause
        )
        
        result = self.execute(query, tuple(usernames))
        return [row['username'] for row in result] if result else []
