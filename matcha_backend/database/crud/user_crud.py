from ..dbmanager import DBManager
import logging
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
from utils.security import SecurityUtils
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)



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
        result = self.select('users', where="id = %s", where_params=(user_id,))
        return result[0] if result else None

    def get_user_by_username(self, username, user_id=None):
        if username:
            
            result = self.select('users', where="username = %s", where_params=(username,))
            logger.info(f"⚡ result = {result}")
        else:
            result = self.select('users', where="user_id = %s", where_params=(user_id,))
            logger.info(f"⚡⚡⚡ result = {result}")
            
        return result[0] if result else None

    def get_user_by_token(self, token, column='*'):
        """Retrieve user by verification token"""
        result = self.select('users',column, where="verification_token = %s", where_params=(token,))
        return result[0] if result else None
    
    def get_user_by_email(self, email):
        """Retrieve user by email"""
        result = self.select('users', where="email = %s", where_params=(email,))
        logger.info(f"⚡ get_user_by_email result = {result}")
        return result[0] if result else None
    
    def get_user_by(self, select_type, field, columns="*"):
        where_clause = f"{select_type} = %s"
        result = self.select('users', columns, where=where_clause, where_params=(field,))
        return result[0] if result else None
    
    # def get_all_users_except_
    
    
    
    
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
    
    def update_last_seen(self, user_id):
        """Update the last_seen timestamp for a user"""
        try:
            query = "UPDATE users SET last_seen = NOW() WHERE id = %s"
            return self.execute(query, (user_id,))
        except Exception as e:
            logger.error(f"Error updating last_seen for user {user_id}: {e}")
            return None
    
    def set_user_online(self, user_id, is_online=True):
        """Set user online/offline status"""
        try:
            if is_online:
                # Update both active status and last_seen when going online
                query = "UPDATE users SET active = TRUE, last_seen = NOW() WHERE id = %s"
                return self.execute(query, (user_id,))
            else:
                # Update last_seen when going offline
                query = "UPDATE users SET active = FALSE, last_seen = NOW() WHERE id = %s"
                return self.execute(query, (user_id,))
        except Exception as e:
            logger.error(f"Error setting user {user_id} online status: {e}")
            return None
    
    def get_user_status(self, user_id):
        """Get user's online status and last_seen"""
        try:
            result = self.select(
                'users',
                columns='id, username, active, last_seen',
                where='id = %s',
                where_params=(user_id,)
            )
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting user status for {user_id}: {e}")
            return None