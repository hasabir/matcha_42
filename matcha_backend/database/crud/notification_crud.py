# database/crud/notification_crud.py
import logging
from database.dbmanager import DBManager

logger = logging.getLogger(__name__)


class Notification(DBManager):
    """
    CRUD operations for notifications table.
    Notification types: 'like', 'unlike', 'match', 'visit', 'message'
    """
    
    def __init__(self, connection_pool):
        super().__init__(connection_pool)

    def create_notification(self, user_id, type, from_user_id, message=None):
        """
        Create a new notification.
        Args:
            user_id: ID of user receiving the notification
            type: Notification type ('like', 'unlike', 'match', 'visit', 'message')
            from_user_id: ID of user who triggered the notification
            message: Optional message text
        """
        query = """
            INSERT INTO notifications (user_id, type, from_user_id, message, is_read, created_at)
            VALUES (%s, %s, %s, %s, FALSE, NOW())
            RETURNING id
        """
        try:
            result = self.execute_query(query, (user_id, type, from_user_id, message), fetch=True)
            if result:
                logger.info(f"Created notification for user {user_id}: {type} from {from_user_id}")
                return result[0]['id']
            return None
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return None

    def get_user_notifications(self, user_id, limit=50, unread_only=False):
        """
        Get notifications for a user.
        Returns list with sender username and profile picture.
        """
        where_clause = "WHERE n.user_id = %s"
        params = [user_id]
        
        if unread_only:
            where_clause += " AND n.is_read = FALSE"
        
        query = f"""
            SELECT 
                n.id,
                n.type,
                n.message,
                n.is_read,
                n.created_at,
                u.username as from_username,
                u.first_name,
                u.last_name,
                p.profile_picture
            FROM notifications n
            JOIN users u ON n.from_user_id = u.id
            LEFT JOIN profiles p ON u.id = p.user_id
            {where_clause}
            ORDER BY n.created_at DESC
            LIMIT %s
        """
        params.append(limit)
        
        try:
            return self.execute_query(query, tuple(params), fetch=True) or []
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return []

    def get_unread_count(self, user_id):
        """Get count of unread notifications."""
        query = "SELECT COUNT(*) as count FROM notifications WHERE user_id = %s AND is_read = FALSE"
        try:
            result = self.execute_query(query, (user_id,), fetch=True)
            return result[0]['count'] if result else 0
        except Exception as e:
            logger.error(f"Error getting unread count: {e}")
            return 0

    def mark_as_read(self, notification_id, user_id):
        """Mark a specific notification as read."""
        query = """
            UPDATE notifications 
            SET is_read = TRUE 
            WHERE id = %s AND user_id = %s
            RETURNING id
        """
        try:
            result = self.execute_query(query, (notification_id, user_id), fetch=True)
            return bool(result)
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False

    def mark_all_as_read(self, user_id):
        """Mark all notifications as read for a user."""
        query = "UPDATE notifications SET is_read = TRUE WHERE user_id = %s AND is_read = FALSE"
        try:
            self.execute_query(query, (user_id,))
            logger.info(f"Marked all notifications as read for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error marking all as read: {e}")
            return False

    def delete_notification(self, notification_id, user_id):
        """Delete a notification."""
        query = "DELETE FROM notifications WHERE id = %s AND user_id = %s RETURNING id"
        try:
            result = self.execute_query(query, (notification_id, user_id), fetch=True)
            return bool(result)
        except Exception as e:
            logger.error(f"Error deleting notification: {e}")
            return False

    def delete_old_notifications(self, days=30):
        """Delete notifications older than specified days."""
        query = """
            DELETE FROM notifications 
            WHERE created_at < NOW() - INTERVAL '%s days'
            RETURNING id
        """
        try:
            result = self.execute_query(query, (days,), fetch=True)
            count = len(result) if result else 0
            logger.info(f"Deleted {count} old notifications")
            return count
        except Exception as e:
            logger.error(f"Error deleting old notifications: {e}")
            return 0
