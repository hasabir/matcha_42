from ..dbmanager import DBManager
import logging


class User(DBManager):
    def __init__(self, connection_pool):
        super().__init__(connection_pool)
    
    def get_user_by_id(self, user_id):
        """Retrieve user by ID"""
        return self.select('users', where='id = %s', params=(user_id,))
    
    def get_user_by_username(self, username):
        """Retrieve user by username"""
        return self.select('users', where='username = %s', params=(username,))
    
    def create_user(self, user_data):
        """Create a new user"""
        # user_data["id"] = 1
        logging.basicConfig(level=logging.INFO)
        logging.info("||||||||||||||||||User Data: %s", user_data, type(user_data))
        return self.insert('users', user_data)
    
    def update_user(self, user_id, user_data):
        """uodate user information"""
        return self.update('users', user_data, where='id = %s', params=(user_id,))
    
    def delete_user(self, user_id):
        """Delete a user by ID"""
        return self.delete('users', where='id = %s', params=(user_id,))
    
    def get_all_users(self):
        """Retrieve all users"""
        return self.select('users')
    