import logging
from ..dbmanager import DBManager

logger = logging.getLogger(__name__)



class Matching(DBManager):
    def __init__(self, connection_pool):
        super().__init__(connection_pool)
        
        
    # def get_potential_matches(user_id, filters=None):
    # """Complex query for matching algorithm"""

# def calculate_distance(lat1, lng1, lat2, lng2):
# def get_common_interests_count(user1_id, user2_id):
# def get_user_fame_rating(user_id):
# def update_fame_rating(user_id, new_rating):