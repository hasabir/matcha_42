from ..dbmanager import DBManager
from psycopg2 import sql

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


    def get_tag_id(self, tag_name):
        try:
            result = self.select('tags', "tag_id", where='tag_name = %s', where_params=(tag_name,))
            return result[0] if result else None
        except Exception as e:
            raise Exception(e)


    def insert_tag(self, tag_name):
        try:
            self.insert('tags', {"tag_name": tag_name}, "nothing")
            return self.get_tag_id(tag_name)
        except Exception as e:
            raise Exception(e)
        # if result: # If the INSERT succeeded and returned an id
        #     return result
        # else: #! If there was a conflict, get the existing id (do i need it?)
        #     return ("Aleready exists")
            # select_query = "SELECT tag_id FROM tags WHERE tag_name = %s;"
            # return self.execute(select_query, (tag_name,))[0]['tag_id']


    def add_user_interests(self, user_id, tag_id):
        return self.insert(table='user_tags', data={"user_id": user_id,
                                         "tag_id": tag_id},
                           on_conflict="nothing")
    def remove_user_interest(self, user_id, tag_id):
        return self.delete(
                table='user_tags',
                where='user_id = %s AND tag_id = %s',
                where_params=(user_id, tag_id)
            )
    # def get_user_interests(user_id):
    # def create_interest_if_not_exists(interest_name):