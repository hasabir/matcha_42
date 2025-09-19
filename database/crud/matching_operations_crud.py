import logging
from ..dbmanager import DBManager

logger = logging.getLogger(__name__)



class Matching(DBManager):
    def __init__(self, connection_pool):
        super().__init__(connection_pool)
        self.table_name = 'connections'
        
    # def get_potential_matches(user_id, filters=None):
    # """Complex query for matching algorithm"""
    
    
    def get_matched_users(self, user_id):
        result = self.select(table=self.table_name,
                              columns='user2_id',
                              where='user1_id = %s',
                              where_params=(user_id,))
        return result[0] if result else None
    
    def unmatche(self, user_id, other_user_id):
        return self.delete(table=self.table_name,
                           where='user1_id = %s AND user2_id = %s',
                           where_params=(user_id, other_user_id))
    
    def matche(self, user1_id, user2_id):
        return self.insert(table=self.table_name,
                           data={"user1_id": user1_id, "user2_id": user2_id},
                           on_conflict="nothing",
                           conflict_target=["user1_id", "user2_id"])

    def are_matched(self, user1_id, user2_id):
        result = self.select(table=self.table_name,
                              columns='user1_id',
                              where='user1_id = %s AND user2_id = %s',
                              where_params=(user1_id, user2_id))
        return bool(result)


# def calculate_distance(lat1, lng1, lat2, lng2):
# def get_common_interests_count(user1_id, user2_id):
# def get_user_fame_rating(user_id):
# def update_fame_rating(user_id, new_rating):