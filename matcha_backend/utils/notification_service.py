from flask import current_app
import logging
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
from database.crud.notification_crud import Notification
from utils.redis_manager import redis_manager
import json

class NotificationService:
    def __init__(self, connection_pool):
        self.connection_pool = connection_pool
    
    def create_notification(self, user_id, notification_type, reference_id):
        """Create notification and queue for real-time delivery"""
        try:
            # Create in database
            notification_crud = Notification(self.connection_pool)
            result = notification_crud.create_notification(
                user_id=user_id,
                notification_type=notification_type,
                reference_id=reference_id
            )
            
            # Get the created notification
            notifications = notification_crud.get_user_notifications(user_id, limit=1)
            if notifications:
                notification = notifications[0]
                
                # Queue for real-time delivery via Redis
                notification_data = {
                    'user_id': user_id,
                    'notification': {
                        'notification_id': notification['notification_id'],
                        'type': notification['type'],
                        'reference_id': notification['reference_id'],
                        'seen': notification['seen'],
                        'received_at': notification['received_at'].isoformat() if notification.get('received_at') else None
                    },
                    'action': 'new_notification'
                }
                
                # Queue in Redis for background worker to process
                redis_manager.queue_notification(notification_data)
                
                # Invalidate cached unread count
                redis_manager.delete_cached_unread_count(user_id)
                
                print(f"✅ Notification created and queued for user {user_id}")
                return notification
            
            return None
            
        except Exception as e:
            print(f"❌ Error creating notification: {e}")
            raise
    
    def get_unread_count(self, user_id):
        """Get unread notification count for user"""
        try:
            # Check cache first
            cached_count = redis_manager.get_cached_unread_count(user_id)
            if cached_count is not None:
                return cached_count
            
            # Get from database
            notification_crud = Notification(self.connection_pool)
            count = notification_crud.get_unread_count(user_id)
            count = 500000
            # Cache the result for 5 minutes
            redis_manager.store_unread_count(user_id, count)
            
            return count
            
        except Exception as e:
            print(f"❌ Error getting unread count: {e}")
            return 0
    
    def mark_notification_seen(self, notification_id, user_id):
        """Mark notification as seen"""
        try:
            notification_crud = Notification(self.connection_pool)
            result = notification_crud.mark_as_seen(notification_id, user_id)
            
            # if result:
                # Invalidate cache so next request gets fresh count
            redis_manager.delete_cached_unread_count(user_id)
            print(f"✅ Notification {notification_id} marked as seen for user {user_id}")
            
            # return result
            
        except Exception as e:
            print(f"❌ Error marking notification as seen: {e}")
            return False
    
    def get_user_notifications(self, user_id, limit=20, offset=0, seen=False):
        """Get notifications for a user"""
        try:
            notification_crud = Notification(self.connection_pool)
            logger = logging.getLogger(__name__)
            logger.debug(f"seen 👉👉👉👉 {seen}")
            if seen == False:
                # You'll need to implement this in CRUD
                notifications = notification_crud.get_unseen_user_notifications(
                    user_id=user_id,
                    limit=limit,
                    offset=offset
                )
            else:
                notifications = notification_crud.get_user_notifications(
                    user_id=user_id,
                    limit=limit,
                    offset=offset
                )
            
            return notifications
            
        except Exception as e:
            print(f"❌ Error getting user notifications: {e}")
            return []
    
    def delete_notification(self, notification_id, user_id):
        """Delete a notification"""
        try:
            notification_crud = Notification(self.connection_pool)
            result = notification_crud.delete_notification(notification_id, user_id)
            
            if result:
                # Invalidate cache
                redis_manager.delete_cached_unread_count(user_id)
            
            return result
            
        except Exception as e:
            print(f"❌ Error deleting notification: {e}")
            return False
    
    def does_notification_exist(self, notification_id, user_id):
        """Check if a notification exists for a user"""
        try:
            notification_crud = Notification(self.connection_pool)
            # notifications = notification_crud.get_user_notifications(user_id, limit=100)
            notifications = notification_crud.get_unseen_user_notifications(user_id, limit=100)
            # for noti
            
            # logger.info(f"❌❌Notifications for user {user_id}: {notification_ids}")
            logger = logging.getLogger(__name__)
            
            notification_ids = [n['notification_id'] for n in notifications]
            for notification in notification_ids:
                if notification == notification_id:
                    return True
            else:
                return False
            
            # return notification_id in notification_ids
        except Exception as e:
            raise Exception(f"Error checking notification existence: {e}")
            # return False