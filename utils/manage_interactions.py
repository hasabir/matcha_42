import logging

from database.crud.matching_operations_crud import Matching


logger = logging.getLogger(__name__)
class ManageInteractions():
    def __init__(self, connection_pool, intractions_crud):
        self.connection_pool = connection_pool
        self.interactions_crud = intractions_crud

    def check_action(self, user_id, liked_id):
        liked_users = self.interactions_crud.get_user_likes()
        if not liked_users or liked_id != liked_users['liked_id']:
            logger.debug(f"👉👉👉👉{liked_users}👈👈👈👈")
            return "like"
        matchin_crud = Matching(self.connection_pool)
        matched_users = matchin_crud.get_matched_users(user_id)
        # if matched_users and 
        return "dislike"