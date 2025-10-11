import logging
from flask_socketio import emit, join_room, leave_room
from flask import current_app, g, request
from flask_socketio import emit, join_room, leave_room

import sys
import os

import jwt
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
from .security import SecurityUtils, auth_guard
# from notification_service import NotificationService
from .notification_service import NotificationService
from .redis_manager import redis_manager
# from notification_service import NotificationService
logger = logging.getLogger(__name__)

def register_socket_events(socketio):
    """Register all Socket.IO event handlers"""
    

    @socketio.on('connect')
    def handle_connect():
        try:
            # Extract token from headers
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                emit('error', {'message': 'No authorization token provided'})
                return False
                
            token = auth_header.split(' ')[1]
            
            # Decode JWT to get user_id
            try:
                payload = SecurityUtils.verify_jwt_token(token)
                user_id = payload['user_id']
            except jwt.ExpiredSignatureError:
                emit('error', {'message': 'Token expired'})
                return False
            except jwt.InvalidTokenError:
                emit('error', {'message': 'Invalid token'})
                return False
                
            logger.debug(f"👉👉👉👉SocketIO connect event: {user_id}")
            
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
                emit('connected', {'message': f'User {user_id} connected successfully'})
            else:
                emit('error', {'message': 'No user_id in token'})
                return False
                
        except Exception as e:
            logging.error(f"Connection error: {e}")
            emit('error', {'message': 'Connection failed'})
            return False



    # @auth_guard
    # @socketio.on('connect')
    # def handle_connect():
    #     try:
    #         # Get user_id from query parameters
    #         user_id = int(request.args['user_id'])
    #         logger.debug(f"👉👉👉👉SocketIO connect event: {int(request.args['user_id'])}")
    #         if user_id:
    #             room = f'user_{user_id}'
    #             join_room(room)
                
    #             # Store user-socket mapping in Redis
    #             redis_manager.store_user_session(user_id, request.sid)
                
    #             # Send current unread count
    #             connection_pool = current_app.config["CONNECTION_POOL"]
    #             notification_service = NotificationService(connection_pool)
    #             unread_count = notification_service.get_unread_count(user_id)
                
    #             emit('unread_count', {'count': unread_count}, room=request.sid)
    #             # Join a room for this specific user
    #             # join_room(f"user_{user_id}")
    #             # print(f'User {user_id} connected with SID: {request.sid}')
    #             emit('connected', {'message': f'User {user_id} connected successfully'})
    #         else:
    #             emit('error', {'message': 'No user_id provided'})
    #     except Exception as e:
    #         logging.error(f"Connection error: {e}")
    #         emit('error', {'message': 'Connection failed'})


    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print('Client disconnected:', request.sid)
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