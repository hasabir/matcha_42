import logging

from database.crud.interactions_crud import Interactions
from database.crud.matching_operations_crud import Matching


logger = logging.getLogger(__name__)
class ManageInteractions():
    def __init__(self, connection_pool, intractions_crud):
        self.connection_pool = connection_pool
        self.interactions_crud = intractions_crud

    def check_action(self, user_id, liked_id):
        liked_users = self.interactions_crud.get_user_likes()
        logger.debug(f"👉👉👉👉{liked_users}👈👈👈👈")
        if not liked_users or liked_id not in liked_users:
            if self.interactions_crud.is_liked_by():
                matching_crud = Matching(self.connection_pool)
                matching_crud.matche(user_id, liked_id)
            return "like"
        matching_crud = Matching(self.connection_pool)
        matched_users_ids = matching_crud.get_matched_users(user_id)
        if matched_users_ids and liked_id in matched_users_ids:
            matching_crud.unmatche(user_id, liked_id)
        return "dislike"
  
    
    
    # def connect_users(self, user1_id, user2_id):
    #     #check if tow users liked each other
        
    #         return "liked"
        
    #     return "no match"
