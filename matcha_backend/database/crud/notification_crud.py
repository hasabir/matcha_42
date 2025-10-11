import logging
from ..dbmanager import DBManager
from psycopg2 import sql

logger = logging.getLogger(__name__)

class Notification(DBManager):
    def __init__(self, connection_pool, user_id=None):
        super().__init__(connection_pool)
        self.user_id = user_id

    def create_notification(self, user_id, notification_type, reference_id=None):
        """Create a new notification"""
        data = {
            'user_id': user_id,
            'type': notification_type,
            'reference_id': reference_id
        }
        return self.insert('notifications', data)

    # def mark_as_seen(self, notification_id=None, user_id=None):
    #     """Mark notifications as seen - can mark specific notification or all for user"""
    #     if notification_id:
    #         return self.update('notifications', {'seen': True}, 
    #                          'notification_id = %s', [notification_id])
    #     elif user_id:
    #         return self.update('notifications', {'seen': True}, 
    #                          'user_id = %s', [user_id])
    #     else:
    #         raise ValueError("Either notification_id or user_id must be provided")

    def mark_as_seen(self, notification_id=None, user_id=None):
        """Mark notifications as seen - can mark specific notification or all for user"""
        try:
            self.update('notifications',
                {'seen': True},
                where="user_id = %s AND notification_id = %s AND seen = FALSE",
                where_params=(user_id, notification_id))
        except Exception as e:
            raise Exception(e)

    def get_user_notifications(self, user_id, limit=50, offset=0, unread_only=False):
        """Get notifications for a user"""
        where = "user_id = %s"
        where_params = (user_id,)  # Use tuple from the start
        
        if unread_only:
            where += " AND seen = FALSE"
        
        query = sql.SQL("""
            SELECT * FROM notifications
            WHERE {where}
            ORDER BY received_at DESC
            LIMIT %s OFFSET %s
        """).format(where=sql.SQL(where))
        
        return self.execute(query, where_params + (limit, offset))
        

    def get_unseen_user_notifications(self, user_id, limit='*', offset=0):
        """Get unseen notifications for a user"""
        logger.info(f"🔑🔑🔑🔑🔑🔑🔑Fetching unseen notifications for user {user_id} with limit {limit} and offset {offset}")
        where = "user_id = %s AND seen = FALSE"
        where_params = (user_id,)
        
        if limit == '*':
            result = self.select('notifications', '*', where, where_params)
        else:
            query = sql.SQL("""
                SELECT * FROM notifications
                WHERE {where}
                ORDER BY received_at DESC
                LIMIT %s OFFSET %s
            """).format(where=sql.SQL(where))
            # Fixed: Added limit and offset to the parameters tuple
            result = self.execute(query, where_params + (limit, offset))
        
        logger.info(f"👉👉👉👉Fetched {len(result)} unseen notifications for user {user_id}")
        return result
        
        
        # return 
    
    def get_unread_count(self, user_id):
        """Get count of unread notifications for a user"""
        result = self.select('notifications', 
                           'COUNT(*)', 
                           where='user_id = %s AND seen = FALSE', 
                           where_params=(user_id, ))
        return result[0]['count'] if result else 0

    def delete_notification(self, notification_id, user_id):
        """Delete a specific notification"""
        return self.delete('notifications', 
                         'notification_id = %s AND user_id = %s', 
                         (notification_id, user_id))

    def delete_all_user_notifications(self, user_id):
        """Delete all notifications for a user"""
        return self.delete('notifications', 
                         'user_id = %s', 
                         (user_id, ))