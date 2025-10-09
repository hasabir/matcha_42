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
        
        

    def set_user_location(self, user_id, latitude, longitude, city=None, country=None, accuracy=None):
        """Insert or update user location with proper UPSERT handling"""
        location_data = {
            "user_id": user_id,
            "latitude": latitude,
            "longitude": longitude,
            "city": city,
            "country": country,
            "accuracy": accuracy
        }
        
        # Filter out None values for update_set
        update_data = {key: value for key, value in location_data.items() 
                    if value is not None and key != 'user_id'}
        
        return self.insert(
            table='user_locations',
            data=location_data,
            on_conflict='UPDATE',
            conflict_target=['user_id'],
            update_set=update_data
        )


    
    def get_user_location(self, user_id):
        """Retrieve user location by user ID"""
        result = self.select('user_locations', where="user_id = %s", where_params=(user_id,))
        location = {}
        if result:
            location = {
                "latitude": result[0]["latitude"],
                "longitude": result[0]["longitude"],
                "city": result[0]["city"],
                "country": result[0]["country"],
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
            
    
