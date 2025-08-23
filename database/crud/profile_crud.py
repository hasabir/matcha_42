from ..dbmanager import DBManager

class Profile(DBManager):
    def __init__(self, connection_pool):
        super().__init__(connection_pool)
    
    def get_profile_by_user_id(self, user_id):
        """Retrieve profile by user ID"""
        result = self.select('profiles', where="user_id = %s", where_params=(user_id,))
        return result[0] if result else None

    def create_profile(self, profile_data):
        """Create a new profile"""
        return self.insert('profiles', profile_data)
    
    def update_profile(self, user_id, profile_data):
        """Update profile information"""
        return self.update('profiles', profile_data, where='user_id = %s', where_params=(user_id,))
    
    def delete_profile(self, user_id):
        """Delete a profile by user ID"""
        return self.delete('profiles', where='user_id = %s', where_params=(user_id,))
    
    def get_all_profiles(self):
        """Retrieve all profiles"""
        return self.select('profiles')