# redis_manager.py
import os
import json
import pickle



import redis
from flask import current_app

class RedisManager:
    def __init__(self):
        self.redis_client = None
        self.app = None

    def init_app(self, app=None):
        """Initialize Redis with the app context"""
        if app is not None:
            self.app = app
            self.redis_client = redis.Redis(
                host=app.config.get('REDIS_HOST', 'localhost'),
                port=app.config.get('REDIS_PORT', 6379),
                db=app.config.get('REDIS_DB', 0),
                decode_responses=True
            )
            # Test the connection
            try:
                self.redis_client.ping()
                print("✅ Redis connection successful")
            except redis.ConnectionError as e:
                print(f"❌ Redis connection failed: {e}")
        else:
            raise ValueError("App instance is required for initialization")

    def get_redis(self):
        """Get Redis client instance"""
        if self.redis_client is None:
            raise RuntimeError("Redis manager not initialized. Call init_app first.")
        return self.redis_client

    # Your existing Redis methods (queue_notification, get_queued_notifications, etc.)
    def queue_notification(self, notification_data):
        """Queue notification for processing"""
        try:
            key = "notification_queue"
            self.redis_client.lpush(key, json.dumps(notification_data))
        except Exception as e:
            print(f"Error queueing notification: {e}")

    def get_queued_notifications(self, count=50):
        """Get queued notifications"""
        try:
            key = "notification_queue"
            notifications = self.redis_client.lrange(key, 0, count-1)
            self.redis_client.ltrim(key, count, -1)  # Remove processed items
            return [json.loads(notification) for notification in notifications]
        except Exception as e:
            print(f"Error getting queued notifications: {e}")
            return []

    def get_cached_unread_count(self, user_id):
        """Get cached unread count"""
        try:
            key = f"unread_count:{user_id}"
            count = self.redis_client.get(key)
            return int(count) if count else None
        except:
            return None

    def store_unread_count(self, user_id, count):
        """Store unread count in cache"""
        try:
            key = f"unread_count:{user_id}"
            self.redis_client.setex(key, 300, count)  # Cache for 5 minutes
        except Exception as e:
            print(f"Error storing unread count: {e}")

    def delete_cached_unread_count(self, user_id):
        """Delete cached unread count"""
        try:
            key = f"unread_count:{user_id}"
            self.redis_client.delete(key)
        except Exception as e:
            print(f"Error deleting cached unread count: {e}")

    def get_user_session(self, user_id):
        """Get user's socket session ID"""
        try:
            key = f"user_session:{user_id}"
            return self.redis_client.get(key)
        except:
            return None
    def store_user_session(self, user_id, socket_id):
        """Store user-socket mapping"""
        try:
            key = f"user_session:{user_id}"
            self.redis_client.setex(key, 3600, socket_id)  # 1 hour expiry
        except Exception as e:
            print(f"Error storing user session: {e}")

    def delete_user_session(self, user_id):
        """Delete user session"""
        try:
            key = f"user_session:{user_id}"
            self.redis_client.delete(key)
        except Exception as e:
            print(f"Error deleting user session: {e}")
# Create a global instance
redis_manager = RedisManager()