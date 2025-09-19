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
            conflict_target=["liker_id", "liked_id"] 
        )
    
    
    def dislike_user(self):
        return self.delete(table='likes',
                           where='liker_id = %s AND liked_id =%s',
                           where_params=(self.user_id, self.other_user_id))
    
    def block_user(self):
        return self.insert(
            table='blocks', 
            data={"blocker_id": self.user_id, "blocked_id": self.other_user_id},
            on_conflict="nothing",
            conflict_target=["blocker_id", "blocked_id"] 
        )
    
    
    def get_user_likes(self, user_id=None):
        if user_id:
            self.user_id = user_id
        result = self.select('likes', columns='liked_id',
                             where='liker_id = %s', where_params=(self.user_id, ))
        # return result[0] if result else None
        return [row['liked_id'] for row in result]
    
    def get_user_likers(self, user_id=None):
        if user_id:
            self.user_id = user_id
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
    
    def get_user_blocks(self):
        result = self.select('blocks', columns='blocked_id',
                             where='blocker_id = %s', where_params=(self.user_id, ))
        # return result[0] if result else None
        return [row['blocked_id'] for row in result]
    
    def report_user(self):
        return self.insert(
            table='reports', 
            data={"reporter_id": self.user_id, "reported_id": self.other_user_id},
            on_conflict="nothing",
            conflict_target=["reporter_id", "reported_id"] 
        )
        
    def get_user_reports(self):
        result = self.select('reports', columns='reported_id',
                             where='reporter_id = %s', where_params=(self.user_id, ))
        # return result[0] if result else None
        return [row['reported_id'] for row in result]
    
    def has_reported(self):
        result = self.select('reports', columns='reporter_id',
                             where='reporter_id = %s AND reported_id = %s',
                             where_params=(self.user_id, self.other_user_id))
        return bool(result)