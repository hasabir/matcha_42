import logging
from flask_socketio import emit, join_room, leave_room
from flask import current_app, g, request
from datetime import datetime, timezone
import time

import sys
import os

import jwt
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
from .security import SecurityUtils, auth_guard
# from notification_service import NotificationService
from .notification_service import NotificationService
from .redis_manager import redis_manager
from .realtime_monitor import log_delay, monitor_delay
# from notification_service import NotificationService
logger = logging.getLogger(__name__)

def register_socket_events(socketio):
    """Register all Socket.IO event handlers"""
    
    @socketio.on('connect')
    def handle_connect(auth=None):
        """
        Handle client connection with proper token authentication.
        The client should pass the JWT via the Socket.IO 'auth' payload.
        Monitors connection delay to ensure < 10 second requirement.
        """
        connect_start = time.time()  # Track connection delay
        try:
            # Try to get token from auth payload first (recommended)
            token = None
            if auth and isinstance(auth, dict) and 'token' in auth:
                token_value = auth['token']
                # Handle both "Bearer TOKEN" and "TOKEN" formats
                if token_value.startswith('Bearer '):
                    token = token_value.split(' ')[1]
                else:
                    token = token_value
                logger.debug(f"✅ Token received via auth payload")
            
            # Fallback to Authorization header (for backward compatibility)
            if not token:
                auth_header = request.headers.get('Authorization')
                if auth_header and auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                    logger.debug(f"✅ Token received via Authorization header")
            
            if not token:
                logger.warning("❌ No authorization token provided")
                emit('error', {'message': 'No authorization token provided'})
                return False
            
            # Decode JWT to get user_id
            try:
                payload = SecurityUtils.verify_jwt_token(token)
                
                # Check if verify_jwt_token returned an error dict
                if isinstance(payload, dict) and 'error' in payload:
                    logger.error(f"❌ Token verification failed: {payload['error']}")
                    emit('error', {'message': payload['error']})
                    return False
                
                user_id = payload.get('user_id')
                
                if not user_id:
                    logger.error(f"❌ No user_id in token payload. Payload: {payload}")
                    emit('error', {'message': 'Invalid token: no user_id'})
                    return False
                    
            except jwt.ExpiredSignatureError:
                logger.warning(f"❌ Expired token")
                emit('error', {'message': 'Token expired'})
                return False
            except jwt.InvalidTokenError as e:
                logger.warning(f"❌ Invalid token: {str(e)}")
                emit('error', {'message': 'Invalid token'})
                return False
            
            logger.info(f"✅ User {user_id} connected via SocketIO (sid: {request.sid})")
            
            # Update user status in database - set online and update last_seen
            try:
                connection_pool = current_app.config.get("CONNECTION_POOL")
                if connection_pool:
                    from database.crud.user_crud import User
                    user_crud = User(connection_pool)
                    user_crud.set_user_online(user_id, True)
                    logger.info(f"✅ Updated user {user_id} status to online")
                    
                    # Broadcast user online status to all connected clients
                    # Important: Use the socketio instance from current_app to ensure broadcast works
                    status_payload = {
                        'user_id': user_id,
                        'is_online': True,
                        'last_seen': datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Get socketio instance from current_app
                    socketio_instance = current_app.config.get("SOCKETIO")
                    if socketio_instance:
                        socketio_instance.emit('user_status_changed', status_payload, broadcast=True)
                        logger.info(f"📢 Broadcasted online status for user {user_id}: {status_payload}")
                    else:
                        logger.warning(f"⚠️ Could not get socketio instance to broadcast online status for user {user_id}")
            except Exception as status_error:
                logger.warning(f"⚠️ Failed to update user status: {status_error}")
            
            # Join user to their personal room
            room = f'user_{user_id}'
            join_room(room)
            logger.debug(f"👤 User {user_id} joined room: {room}")
            
            # Store user-socket mapping in Redis
            try:
                redis_manager.store_user_session(user_id, request.sid)
                logger.debug(f"💾 Stored session for user {user_id}")
            except Exception as redis_error:
                logger.warning(f"⚠️ Failed to store session in Redis: {redis_error}")
                # Don't fail the connection if Redis is down
            
            # Send current unread count
            try:
                connection_pool = current_app.config.get("CONNECTION_POOL")
                if connection_pool:
                    notification_service = NotificationService(connection_pool)
                    unread_count = notification_service.get_unread_count(user_id)
                    emit('unread_count', {'count': unread_count}, room=request.sid)
                    logger.debug(f"📬 Sent unread count ({unread_count}) to user {user_id}")
            except Exception as notif_error:
                logger.error(f"⚠️ Failed to send unread count: {notif_error}")
                # Don't fail the connection if notification service has issues
            
            # Confirm successful connection
            emit('connected', {
                'message': f'Successfully connected to notification service',
                'user_id': user_id
            })
            
            # Track connection delay (10-second requirement)
            log_delay('socket_connection', connect_start, user_id=user_id, 
                     additional_info={'sid': request.sid})
            
            return True
                
        except Exception as e:
            logger.exception(f"❌ Unexpected error during SocketIO connection")
            emit('error', {'message': 'Connection failed due to server error'})
            # Track failed connection delay
            log_delay('socket_connection_failed', connect_start, 
                     additional_info={'error': str(e)})
            return False


    @socketio.on('disconnect')
    def handle_disconnect():
        """
        Handle client disconnection and clean up session data.
        """
        try:
            sid = request.sid
            logger.info(f"🔌 Client disconnected: {sid}")
            
            # Try to find and clean up user session from Redis
            try:
                # Get user_id from Redis using socket_id
                user_id = redis_manager.get_user_by_session(sid)
                
                if user_id:
                    logger.info(f"👤 User {user_id} disconnected (sid: {sid})")
                    
                    # Ensure user_id is an integer (Redis returns strings)
                    user_id_int = int(user_id) if isinstance(user_id, (str, bytes)) else user_id
                    
                    # Remove this specific socket from user's connections
                    remaining_connections = redis_manager.remove_user_session(user_id_int, sid)
                    logger.info(f"📊 User {user_id_int} has {remaining_connections} remaining connections")
                    
                    # Only set user offline if they have NO remaining connections
                    if remaining_connections == 0:
                        # Update user status in database - set offline and update last_seen
                        connection_pool = current_app.config.get("CONNECTION_POOL")
                        if connection_pool:
                            from database.crud.user_crud import User
                            user_crud = User(connection_pool)
                            user_status = user_crud.set_user_online(user_id_int, False)
                            logger.info(f"✅ Updated user {user_id_int} status to offline (no remaining connections)")
                            
                            # Broadcast user offline status to all connected clients
                            # Important: Use the socketio instance from current_app to ensure broadcast works
                            status_payload = {
                                'user_id': user_id_int,
                                'is_online': False,
                                'last_seen': datetime.now(timezone.utc).isoformat()
                            }
                            
                            # Get socketio instance from current_app
                            socketio_instance = current_app.config.get("SOCKETIO")
                            if socketio_instance:
                                socketio_instance.emit('user_status_changed', status_payload, broadcast=True)
                                logger.info(f"📢 Broadcasted offline status for user {user_id_int}: {status_payload}")
                            else:
                                logger.error(f"❌ Could not get socketio instance to broadcast offline status for user {user_id_int}")
                    else:
                        logger.info(f"✅ User {user_id_int} still has {remaining_connections} active connection(s), keeping online status")
                else:
                    logger.debug(f"🧹 No user_id found for sid: {sid}")
                    
            except Exception as cleanup_error:
                logger.warning(f"⚠️ Error during session cleanup: {cleanup_error}")
                import traceback
                logger.warning(traceback.format_exc())
                
        except Exception as e:
            logger.error(f"❌ Error in disconnect handler: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    @socketio.on('user_logout')
    def handle_user_logout():
        """
        Handle explicit user logout event - update status immediately and clear ALL connections.
        This ensures other users see the offline status right away when user logs out.
        Returns acknowledgement to client.
        """
        try:
            sid = request.sid
            logger.info(f"🚪 User logout event received: {sid}")
            
            # Get user_id from Redis
            user_id = redis_manager.get_user_by_session(sid)
            
            if user_id:
                logger.info(f"👤 User {user_id} logging out (sid: {sid})")
                
                # Ensure user_id is an integer (Redis returns strings)
                user_id_int = int(user_id) if isinstance(user_id, (str, bytes)) else user_id
                
                # Update user status in database - set offline and update last_seen
                connection_pool = current_app.config.get("CONNECTION_POOL")
                if connection_pool:
                    from database.crud.user_crud import User
                    user_crud = User(connection_pool)
                    user_crud.set_user_online(user_id_int, False)
                    logger.info(f"✅ Updated user {user_id_int} status to offline (logout)")
                    
                    # Broadcast user offline status to all connected clients
                    # Important: Use the socketio instance from current_app to ensure broadcast works
                    status_payload = {
                        'user_id': user_id_int,
                        'is_online': False,
                        'last_seen': datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Get socketio instance from current_app
                    socketio_instance = current_app.config.get("SOCKETIO")
                    if socketio_instance:
                        socketio_instance.emit('user_status_changed', status_payload, broadcast=True)
                        logger.info(f"📢 Broadcasted offline status for user {user_id_int} (logout): {status_payload}")
                    else:
                        logger.error(f"❌ Could not get socketio instance to broadcast offline status for user {user_id_int}")
                
                # Clear ALL Redis sessions for this user (all tabs/browsers)
                redis_manager.remove_user_session(user_id_int, socket_id=None)
                logger.info(f"🧹 Cleaned up ALL Redis sessions for user {user_id_int} (logout)")
                
                return {'status': 'success', 'user_id': user_id_int}
            else:
                logger.warning(f"⚠️ Logout event received but no user_id found for sid: {sid}")
                return {'status': 'error', 'message': 'No user_id found'}
                
        except Exception as e:
            logger.error(f"❌ Error in user_logout handler: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'status': 'error', 'message': str(e)}
    
    @socketio.on('heartbeat')
    def handle_heartbeat():
        """
        Handle heartbeat from client to update last_seen timestamp.
        Clients should send this every 1-2 minutes to keep their online status fresh.
        """
        try:
            sid = request.sid
            
            # Get user_id from Redis
            user_id = redis_manager.get_user_by_session(sid)
            
            if user_id:
                # Update last_seen timestamp
                connection_pool = current_app.config.get("CONNECTION_POOL")
                if connection_pool:
                    from database.crud.user_crud import User
                    user_crud = User(connection_pool)
                    user_crud.update_last_seen(user_id)
                    logger.debug(f"💓 Heartbeat from user {user_id} - last_seen updated")
                    
                    # Acknowledge heartbeat
                    emit('heartbeat_ack', {'status': 'ok', 'timestamp': datetime.now(timezone.utc).isoformat()})
            else:
                logger.warning(f"⚠️ Heartbeat received but no user_id found for sid: {sid}")
                
        except Exception as e:
            logger.error(f"❌ Error handling heartbeat: {e}")
    
    # When creating a notification, emit to specific user room
    # def send_notification_to_user(user_id, notification_data):
    #     emit('notification', notification_data, room=f"user_{user_id}")
        # or emit to a specific socket id if you're tracking them
    
    
    # @socketio.on('connect')
    # # @auth_guard
    # def handle_connect():
    #     logger.debug(f"👉👉👉👉SocketIO connect event: {request.sid}")
    #     """Handle client connection"""
    #     try:
    #         # user_id = g.user_id
    #         # logger.debug(f"User ID from auth_guard: {user_id}")
    #         # In real implementation, you'd authenticate here
    #         print('Client connected:', request.sid)
    #         emit('connected', {'message': 'Successsssfully connected to notification service'})
    #     except Exception as e:
    #         logging.error(f"Connection error: {e}")
    #         emit('error', {'message': '❌Connection failed'})
        

    @socketio.on('join_notifications')
    def handle_join_notifications(data):
        """Join user to their notification room"""
        try:
            user_id = data.get('user_id')
            if user_id:
                room = f'user_{user_id}'
                join_room(room)
                
                # Store user-socket mapping in Redis
                redis_manager.store_user_session(user_id, request.sid)
                
                # Send current unread count
                connection_pool = current_app.config["CONNECTION_POOL"]
                notification_service = NotificationService(connection_pool)
                unread_count = notification_service.get_unread_count(user_id)
                
                emit('unread_count', {'count': unread_count}, room=request.sid)
                print(f'User {user_id} joined room {room}')
                
        except Exception as e:
            logging.error(f"Error joining notifications room: {e}")
            emit('error', {'message': 'Failed to join notifications'})

    

    # @socketio.on('leave_notifications')
    # def handle_leave_notifications(data):
    #     """Leave notification room"""
    #     try:
    #         user_id = data.get('user_id')
    #         if user_id:
    #             room = f'user_{user_id}'
    #             leave_room(room)
    #             redis_manager.delete_user_session(user_id)
    #             print(f'User {user_id} left room {room}')
                
    #     except Exception as e:
    #         logging.error(f"Error leaving notifications room: {e}")

    # @socketio.on('mark_notification_seen')
    # @auth_guard
    # def handle_mark_seen(data):
    #     """Mark notification as seen via WebSocket"""
    #     try:
    #         notification_id = data.get('notification_id')
    #         user_id = data.get('user_id')
            
    #         if notification_id and user_id:
    #             connection_pool = current_app.config["CONNECTION_POOL"]
    #             notification_service = NotificationService(connection_pool)
                
    #             result = notification_service.mark_notification_seen(
    #                 notification_id=notification_id,
    #                 user_id=user_id
    #             )
                
    #             if result:
    #                 # Send updated unread count
    #                 unread_count = notification_service.get_unread_count(user_id)
    #                 emit('unread_count_updated', {'count': unread_count}, room=f'user_{user_id}')
    #                 emit('notification_seen', {'success': True, 'notification_id': notification_id})
    #             else:
    #                 emit('error', {'message': 'Failed to mark notification as seen'})
                    
    #     except Exception as e:
    #         logging.error(f"Error marking notification as seen via socket: {e}")
    #         emit('error', {'message': 'Internal server error'})