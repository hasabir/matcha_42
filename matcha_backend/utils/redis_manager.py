# redis_manager.py
import os
import json
import pickle
import time
import logging

import redis
from flask import current_app

logger = logging.getLogger(__name__)

class RedisManager:
    def __init__(self):
        self.redis_client = None
        self.app = None

    def init_app(self, app=None):
        """Initialize Redis with the app context and retry logic"""
        if app is None:
            raise ValueError("App instance is required for initialization")
        
        self.app = app
        redis_host = app.config.get('REDIS_HOST', 'localhost')
        redis_port = app.config.get('REDIS_PORT', 6379)
        redis_db = app.config.get('REDIS_DB', 0)
        
        # Retry logic for Docker container startup
        max_retries = 30
        retry_delay = 2  # seconds
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"🔄 Attempting to connect to Redis (attempt {attempt}/{max_retries})...")
                
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                
                # Test the connection
                self.redis_client.ping()
                logger.info(f"✅ Redis connection successful (host: {redis_host}:{redis_port})")
                return
                
            except redis.ConnectionError as e:
                error_msg = str(e)
                
                # Check if it's a DNS resolution error or connection refused
                if "Temporary failure in name resolution" in error_msg or "Name or service not known" in error_msg:
                    logger.warning(f"⏳ Redis DNS resolution failed for host '{redis_host}' (attempt {attempt}/{max_retries}). Retrying in {retry_delay}s...")
                elif "Connection refused" in error_msg:
                    logger.warning(f"⏳ Redis not ready yet (attempt {attempt}/{max_retries}). Retrying in {retry_delay}s...")
                else:
                    logger.warning(f"⏳ Redis connection error: {error_msg} (attempt {attempt}/{max_retries}). Retrying in {retry_delay}s...")
                
                if attempt < max_retries:
                    time.sleep(retry_delay)
                else:
                    logger.error(f"❌ Redis connection failed after {max_retries} attempts")
                    # Don't raise exception, continue without Redis (degraded mode)
                    self.redis_client = None
                    logger.warning("⚠️  Running in degraded mode without Redis")
                    
            except Exception as e:
                logger.error(f"❌ Unexpected Redis error: {str(e)}")
                if attempt < max_retries:
                    time.sleep(retry_delay)
                else:
                    self.redis_client = None
                    logger.warning("⚠️  Running in degraded mode without Redis")

    def get_redis(self):
        """Get Redis client instance"""
        if self.redis_client is None:
            logger.warning("⚠️  Redis client not available - running in degraded mode")
            return None
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
        """Get user's socket session IDs (returns list of all active socket IDs)"""
        try:
            key = f"user_sessions:{user_id}"
            socket_ids = self.redis_client.smembers(key)
            return list(socket_ids) if socket_ids else []
        except:
            return []
    
    def store_user_session(self, user_id, socket_id):
        """Store user-socket mapping (supports multiple connections per user)"""
        try:
            # Add socket_id to user's set of connections
            key = f"user_sessions:{user_id}"
            self.redis_client.sadd(key, socket_id)
            self.redis_client.expire(key, 3600)  # Reset expiry to 1 hour
            
            # Store socket_id -> user_id for reverse lookup
            reverse_key = f"socket_session:{socket_id}"
            self.redis_client.setex(reverse_key, 3600, user_id)  # 1 hour expiry
            
            logger.debug(f"✅ Stored session: user {user_id} has socket {socket_id}")
        except Exception as e:
            logger.error(f"Error storing user session: {e}")

    def get_user_by_session(self, socket_id):
        """Get user ID from socket session ID"""
        try:
            key = f"socket_session:{socket_id}"
            return self.redis_client.get(key)
        except:
            return None

    def remove_user_session(self, user_id, socket_id=None):
        """Remove specific socket from user's sessions or all if socket_id is None"""
        try:
            if socket_id:
                # Remove specific socket from user's set
                key = f"user_sessions:{user_id}"
                self.redis_client.srem(key, socket_id)
                
                # Delete reverse mapping
                reverse_key = f"socket_session:{socket_id}"
                self.redis_client.delete(reverse_key)
                
                # Get remaining connections count
                remaining = self.redis_client.scard(key)
                logger.debug(f"🧹 Removed socket {socket_id} from user {user_id}. Remaining connections: {remaining}")
                
                # If no more connections, delete the set
                if remaining == 0:
                    self.redis_client.delete(key)
                    logger.debug(f"🧹 Deleted empty connection set for user {user_id}")
                
                return remaining
            else:
                # Remove all connections for user
                key = f"user_sessions:{user_id}"
                socket_ids = self.redis_client.smembers(key)
                
                # Delete all reverse mappings
                for sid in socket_ids:
                    reverse_key = f"socket_session:{sid}"
                    self.redis_client.delete(reverse_key)
                
                # Delete user's connection set
                self.redis_client.delete(key)
                logger.debug(f"🧹 Deleted all connections for user {user_id}")
                return 0
        except Exception as e:
            logger.error(f"Error removing user session: {e}")
            return None
    
    def get_connection_count(self, user_id):
        """Get the number of active socket connections for a user"""
        try:
            key = f"user_sessions:{user_id}"
            return self.redis_client.scard(key)
        except Exception as e:
            logger.error(f"Error getting connection count: {e}")
            return 0

    def delete_user_session(self, user_id):
        """Delete user session (alias for compatibility)"""
        self.remove_user_session(user_id)
# Create a global instance
redis_manager = RedisManager()