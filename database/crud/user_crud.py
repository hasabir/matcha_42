from ..dbmanager import DBManager
import logging
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
from utils.security import SecurityUtils

class User(DBManager):
    def __init__(self, connection_pool):
        super().__init__(connection_pool)
    

    def create_user(self, user_data):
        """Create a new user"""
        user_data['password'] = SecurityUtils.password_hash(user_data['password'])
        logging.basicConfig(level=logging.INFO)
        logging.info("||||||||||||||||||User Data: %s", user_data, type(user_data))
        return self.insert('users', user_data)
    

    def update_user(self, user_id, user_data):
        """uodate user information"""
        return self.update('users', user_data, where='id = %s', params=(user_id,))
    

    def delete_user(self, user_id):
        """Delete a user by ID"""
        return self.delete('users', where='id = %s', params=(user_id,))


    def get_user_by_id(self, user_id):
        """Retrieve user by ID"""
        return self.select('users', where='id = %s', params=(user_id,))
    

    def get_user_by_username(self, username):
        result = self.select('users', where="username = %s", where_params=(username,))
        return result[0] if result else None

    
    def get_all_users(self):
        """Retrieve all users"""
        return self.select('users')
    