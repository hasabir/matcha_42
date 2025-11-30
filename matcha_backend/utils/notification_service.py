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
        self.notification_crud = Notification(connection_pool)
    
    def create_notification(self, user_id, notification_type, reference_id=None, message=None):
        """Create notification and queue for real-time delivery"""
        try:
            # Create in database
            result = self.notification_crud.create_notification(
                user_id=user_id,
                notification_type=notification_type,
                reference_id=reference_id
            )
            
            # If result is None, notification was skipped (too soon after previous one)
            if result is None:
                logging.info(f"⚠️ Notification skipped to prevent duplicate for user {user_id}, type: {notification_type}")
                return None
            
            # Get the created notification
            notifications = self.notification_crud.get_user_notifications(user_id, limit=1)
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
                
                logging.info(f"✅ Notification created and queued for user {user_id}")
                return notification
            
            return None
            
        except Exception as e:
            logging.error(f"❌ Error creating notification: {str(e)}")
            raise
    
    def get_notifications(self, user_id):
        """Get all notifications for a user"""
        try:
            notifications = self.notification_crud.get_user_notifications(user_id)
            if notifications is None:
                notifications = []
            
            # Ensure timestamps are properly serialized to ISO format
            for notification in notifications:
                if notification.get('received_at') and hasattr(notification['received_at'], 'isoformat'):
                    notification['received_at'] = notification['received_at'].isoformat()
            
            logging.info(f"✅ Retrieved {len(notifications)} notifications for user {user_id}")
            return notifications
        except Exception as e:
            logging.error(f"❌ Error in get_notifications: {str(e)}")
            return []
    
    def get_unread_count(self, user_id):
        """Get unread notification count for user"""
        try:
            # Check cache first
            cached_count = redis_manager.get_cached_unread_count(user_id)
            if cached_count is not None:
                logging.debug(f"📦 Using cached unread count for user {user_id}: {cached_count}")
                return cached_count
            
            # Get from database
            count = self.notification_crud.get_unread_count(user_id)
            
            # Cache the result for 5 minutes
            redis_manager.store_unread_count(user_id, count)
            
            logging.info(f"✅ Unread count for user {user_id}: {count}")
            return count
            
        except Exception as e:
            logging.error(f"❌ Error getting unread count: {str(e)}")
            return 0
    
    def mark_as_seen(self, notification_id, user_id):
        """Mark notification as seen"""
        try:
            result = self.notification_crud.mark_as_seen(notification_id, user_id)
            
            if result:
                # Invalidate cache so next request gets fresh count
                redis_manager.delete_cached_unread_count(user_id)
                logging.info(f"✅ Notification {notification_id} marked as seen for user {user_id}")
            
            return result
            
        except Exception as e:
            logging.error(f"❌ Error marking notification as seen: {str(e)}")
            return False
    
    def mark_all_as_seen(self, user_id):
        """Mark all notifications as seen for a user"""
        try:
            result = self.notification_crud.mark_all_as_seen(user_id)
            
            if result:
                # Invalidate cache
                redis_manager.delete_cached_unread_count(user_id)
                logging.info(f"✅ All notifications marked as seen for user {user_id}")
            
            return result
            
        except Exception as e:
            logging.error(f"❌ Error marking all as seen: {str(e)}")
            return False
    
    def mark_notification_seen(self, notification_id, user_id):
        """Legacy method name - calls mark_as_seen for backward compatibility"""
        return self.mark_as_seen(notification_id, user_id)
    
    def get_user_notifications(self, user_id, limit=20, offset=0, seen=False):
        """Get notifications for a user with filtering"""
        try:
            logger = logging.getLogger(__name__)
            logger.debug(f"Getting notifications for user {user_id}, seen={seen}, limit={limit}")
            
            if seen == False:
                # Get only unseen notifications
                notifications = self.notification_crud.get_unseen_user_notifications(
                    user_id=user_id,
                    limit=limit,
                    offset=offset
                )
            else:
                # Get all notifications
                notifications = self.notification_crud.get_user_notifications(
                    user_id=user_id,
                    limit=limit,
                    offset=offset
                )
            
            logging.info(f"✅ Retrieved {len(notifications)} notifications for user {user_id}")
            return notifications
            
        except Exception as e:
            logging.error(f"❌ Error getting user notifications: {str(e)}")
            return []
    
    def delete_notification(self, notification_id, user_id):
        """Delete a notification"""
        try:
            result = self.notification_crud.delete_notification(notification_id, user_id)
            
            if result:
                # Invalidate cache
                redis_manager.delete_cached_unread_count(user_id)
                logging.info(f"✅ Notification {notification_id} deleted for user {user_id}")
            
            return result
            
        except Exception as e:
            logging.error(f"❌ Error deleting notification: {str(e)}")
            return False
    
    def delete_all_user_notifications(self, user_id):
        """Delete all notifications for a user"""
        try:
            result = self.notification_crud.delete_all_user_notifications(user_id)
            
            if result:
                # Invalidate cache
                redis_manager.delete_cached_unread_count(user_id)
                logging.info(f"✅ All notifications deleted for user {user_id}")
            
            return result
            
        except Exception as e:
            logging.error(f"❌ Error deleting all notifications: {str(e)}")
            return False
    
    def does_notification_exist(self, notification_id, user_id):
        """Check if a notification exists for a user"""
        try:
            # Get unseen notifications to check
            notifications = self.notification_crud.get_unseen_user_notifications(user_id, limit=100)
            
            notification_ids = [n['notification_id'] for n in notifications]
            exists = notification_id in notification_ids
            
            if exists:
                logging.debug(f"✅ Notification {notification_id} exists for user {user_id}")
            else:
                logging.debug(f"❌ Notification {notification_id} does not exist for user {user_id}")
            
            return exists
            
        except Exception as e:
            logging.error(f"❌ Error checking notification existence: {str(e)}")
            raise Exception(f"Error checking notification existence: {e}")