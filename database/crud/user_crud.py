from ..dbmanager import DBManager
import logging
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
from utils.security import SecurityUtils
logging.basicConfig(level=logging.INFO)

class User(DBManager):
    def __init__(self, connection_pool):
        super().__init__(connection_pool)
    

    def create_user(self, user_data):
        """Create a new user"""
        user_data['password'] = SecurityUtils.password_hash(user_data['password'])
        return self.insert('users', user_data)
    

    def update_user(self, set_data, username):
        """Update user information"""
        logging.debug(f"****************************Updating user set_data: {set_data}")
        return self.update('users', set_data, where="username = %s", where_params=(username,))

    def delete_user(self, user_id):
        """Delete a user by ID"""
        return self.delete('users', where='id = %s', where_params=(user_id,))


    def get_user_by_id(self, user_id):
        """Retrieve user by ID"""
        return self.select('users', where='id = %s', params=(user_id,))
    

    def get_user_by_username(self, username):
        result = self.select('users', where="username = %s", where_params=(username,))
        return result[0] if result else None

    def get_user_by_token(self, token, column='*'):
        """Retrieve user by verification token"""
        result = self.select('users',column, where="verification_token = %s", where_params=(token,))
        return result[0] if result else None
    
    
    
    
    def get_all_users(self):
        """Retrieve all users"""
        return self.select('users')
    
    def verify_user(self, email):
        """Verify user by email"""
        return self.update('users', {'verified': True}, where='email = %s', params=(email,))
    
    
    def delet_all_users(self):
        """Drop the users table"""
        query = "DELETE FROM users"
        return self.execute(query)