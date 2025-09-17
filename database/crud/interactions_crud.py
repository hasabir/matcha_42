import logging
from ..dbmanager import DBManager
from psycopg2 import sql

logger = logging.getLogger(__name__)

class Interactions(DBManager):
    def __init__(self, connection_pool, user_id, other_user_id):
        super().__init__(connection_pool)
        self.user_id = user_id
        self.other_user_id = other_user_id
    
    
    def like_user(self):
        return self.insert(
            table='likes', 
            data={"liker_id": self.user_id, "liked_id": self.other_user_id},
            on_conflict="nothing",
            conflict_target=["liker_id", "liked_id"]  # Add this line
        )
    
    
    def dislike_user(self):
        return self.delete(table='likes',
                           where='liker_id = %s AND liked_id =%s',
                           where_params=(self.user_id, self.other_user_id))
    
    
    def get_user_likes(self):
        result = self.select('likes', columns='liked_id',
                             where='liker_id = %s', where_params=(self.user_id, ))
        # return result[0] if result else None
        return [row['liked_id'] for row in result]
    
    def get_user_likers(self):
        result = self.select('likes', columns='liker_id',
                             where='liked_id = %s', where_params=(self.user_id, ))
        # return result[0] if result else None
        return [row['liker_id'] for row in result]
    
    def is_liked_by(self):
        result = self.select('likes', columns='liker_id',
                             where='liker_id = %s AND liked_id = %s',
                             where_params=(self.other_user_id, self.user_id))
        return bool(result)
    
    def is_blocked(self):
        result = self.select('blocks', columns='blocker_id',
                             where='blocker_id = %s AND blocked_id = %s',
                             where_params=(self.other_user_id, self.user_id))
        logger.debug(f"👉👉👉👉Blocked check result: {result}👈👈👈👈")
        return bool(result)