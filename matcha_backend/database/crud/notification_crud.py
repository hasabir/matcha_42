import logging
from ..dbmanager import DBManager
from psycopg2 import sql

logger = logging.getLogger(__name__)

class Notification(DBManager):
    def __init__(self, connection_pool, user_id=None):
        super().__init__(connection_pool)
        self.sender_id = user_id

    def create_notification(self, sender_id, notification_type, receiver_id):
        """Create a new notification"""
        data = {
            'sender_id': sender_id,
            'type': notification_type,
            'receiver_id': receiver_id
        }
        return self.insert('notifications', data)

    def mark_as_seen(self, notification_id=None, receiver_id=None):
        """Mark notifications as seen - can mark specific notification or all for user"""
        try:
            self.update('notifications',
                {'seen': True},
                where="receiver_id = %s AND notification_id = %s AND seen = FALSE",
                where_params=(receiver_id, notification_id))
        except Exception as e:
            raise Exception(e)
        
        # if notification_id:
        #     return self.update('notifications', {'seen': True}, 
        #                      'notification_id = %s', [notification_id])
        # elif user_id:
        #     return self.update('notifications', {'seen': True}, 
        #                      'user_id = %s', [user_id])
        # else:
        #     raise ValueError("Either notification_id or user_id must be provided")

    def get_user_notifications(self, receiver_id, limit=50, offset=0, unread_only=False):
        """Get notifications for a user"""
        where = "receiver_id = %s"
        where_params = [receiver_id]
        
        if unread_only:
            where += " AND seen = FALSE"
            
        query = sql.SQL("""
            SELECT * FROM notifications 
            WHERE {where} 
            ORDER BY received_at DESC 
            LIMIT %s OFFSET %s
        """).format(where=sql.SQL(where))
        
        return self.execute(query, where_params + [limit, offset])

    def get_unseen_user_notifications(self, receiver_id, limit='*', offset=0):
        """Get unseen notifications for a user"""
        where = "receiver_id = %s AND seen = FALSE"
        where_params = (receiver_id, )
        if limit == '*':
            result = self.select('notifications', '*', where, where_params)
        else:
            query = sql.SQL("""
                SELECT * FROM notifications 
                WHERE {where} 
                ORDER BY received_at DESC 
                LIMIT %s OFFSET %s
            """).format(where=sql.SQL(where))
            result = self.execute(query, where_params + [limit, offset])
        return result
        
        
        # return 
    
    def get_unread_count(self, reciever_id):
        """Get count of unread notifications for a user"""
        result = self.select('notifications', 
                           'COUNT(*)', 
                           where='reciever_id = %s AND seen = FALSE', 
                           where_params=(reciever_id, ))
        return result[0]['count'] if result else 0

    def delete_notification(self, notification_id, reciever_id):
        """Delete a specific notification"""
        return self.delete('notifications', 
                         'notification_id = %s AND reciever_id = %s', 
                         (notification_id, reciever_id))

    def delete_all_user_notifications(self, reciever_id):
        """Delete all notifications for a user"""
        return self.delete('notifications', 
                         'reciever_id = %s', 
                         (reciever_id, ))