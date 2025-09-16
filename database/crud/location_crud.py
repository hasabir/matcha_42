from ..dbmanager import DBManager
import logging
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
from utils.security import SecurityUtils
logging.basicConfig(level=logging.INFO)

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

    # def set_user_location(self, location_data):
    #     """Insert or update user location with proper UPSERT handling"""
    #     user_id = location_data.get('user_id')
        # if not user_id:
        #     raise ValueError("user_id is required")
        
        # update_data = {key: value for key, value in location_data.items() if value is not None and key != 'user_id'}
        
        # return self.insert(
        #     table='user_locations',
        #     data=location_data,
        #     on_conflict='UPDATE',
        #     conflict_target=['user_id'],
        #     update_set=update_data
        # )


    
        # except Exception as e:
        #     logging.error(f"Error setting location for user {user_id}: {e}")
        #     raise
    
    def get_user_location(self, user_id):
        """Retrieve user location by user ID"""
        result = self.select('user_locations', where="user_id = %s", where_params=(user_id,))
        return result[0] if result else None