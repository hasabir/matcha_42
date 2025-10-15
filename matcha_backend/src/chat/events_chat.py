import logging
from flask_socketio import emit, join_room, leave_room
from flask import current_app, request
import sys
import os
import jwt

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
from database.crud.interactions_crud import Interactions
from utils.security import SecurityUtils, auth_guard
from utils.notification_service import NotificationService
from utils.redis_manager import redis_manager
from database.crud.chat_crud import Chat
from database.crud.matching_operations_crud import Matching

logger = logging.getLogger(__name__)


def get_chat_room(user_id_1, user_id_2):
    """Generate consistent chat room name for two users"""
    return f'chat_{min(user_id_1, user_id_2)}_{max(user_id_1, user_id_2)}'


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
                
            logger.debug(f"👉 SocketIO connect event: {user_id}")
            
            if user_id:
                # Store user-socket mapping in Redis
                redis_manager.store_user_session(user_id, request.sid)
                
                # Join user's personal room for notifications
                personal_room = f'user_{user_id}'
                join_room(personal_room)
                
                emit('connected', {
                    'message': f'User {user_id} connected successfully',
                    'user_id': user_id
                })
            else:
                emit('error', {'message': 'No user_id in token'})
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during SocketIO connect: {e}")
            emit('error', {'message': 'Internal server error'})
            return False
    

    @socketio.on('join_chat')
    def handle_join_chat(data):
        """Join a chat room with another user"""
        try:
            user_id = data.get('user_id')
            other_user_id = data.get('other_user_id')
            
            if not user_id or not other_user_id:
                emit('error', {'message': 'Missing user_id or other_user_id'})
                return
            
            connection_pool = current_app.config.get("CONNECTION_POOL")
            if not connection_pool:
                emit("error", {"message": "Database connection pool is not available"})
                return
            
            # Verify users are matched
            matching_operation = Matching(connection_pool=connection_pool)
            if not matching_operation.are_matched(user_id, other_user_id):
                emit('error', {'message': 'You can only chat with matched users'})
                return
            
            # Check for blocks
            interactions_crud = Interactions(connection_pool, user_id, other_user_id)
            if interactions_crud.is_blocked():
                emit('error', {'message': 'You are blocked by this user'})
                return
            if interactions_crud.did_i_block():
                emit('error', {'message': 'You have blocked this user'})
                return
            
            # Generate and join chat room
            room = get_chat_room(user_id, other_user_id)
            join_room(room)
            
            logger.info(f"User {user_id} joined chat room {room}")
            emit('chat_joined', {
                'room': room,
                'user_id': user_id,
                'other_user_id': other_user_id
            })
            
        except Exception as e:
            logger.error(f"❌ Error joining chat: {e}")
            emit('error', {'message': 'Internal server error'})
    
    
    @socketio.on('leave_chat')
    def handle_leave_chat(data):
        """Leave a chat room"""
        try:
            user_id = data.get('user_id')
            other_user_id = data.get('other_user_id')
            
            if not user_id or not other_user_id:
                emit('error', {'message': 'Missing user_id or other_user_id'})
                return
            
            room = get_chat_room(user_id, other_user_id)
            leave_room(room)
            
            logger.info(f"User {user_id} left chat room {room}")
            emit('chat_left', {'room': room})
            
        except Exception as e:
            logger.error(f"❌ Error leaving chat: {e}")
            emit('error', {'message': 'Internal server error'})
    
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """Send a message to another user"""
        try:
            connection_pool = current_app.config.get("CONNECTION_POOL")
            if not connection_pool:
                emit("error", {"message": "Database connection pool is not available"})
                return
            
            sender_id = data.get('sender_id')
            receiver_id = data.get('receiver_id')
            content = data.get('content')
            
            if not sender_id or not receiver_id or not content:
                emit('error', {'message': 'Missing required fields'})
                return
            
            # Verify users are still matched
            matching_operation = Matching(connection_pool=connection_pool)
            if not matching_operation.are_matched(sender_id, receiver_id):
                emit('error', {'message': 'You can only message matched users'})
                return
            
            # Check for blocks
            interactions_crud = Interactions(connection_pool, sender_id, receiver_id)
            if interactions_crud.is_blocked() or interactions_crud.did_i_block():
                emit('error', {'message': 'Cannot send message to blocked user'})
                return
            
            # Create message in database
            chat_crud = Chat(connection_pool=connection_pool)
            message = chat_crud.create_message(sender_id, receiver_id, content)
            
            if not message:
                emit('error', {'message': 'Failed to create message'})
                return
            
            # Prepare message data
            message_data = {
                'message_id': message['id'],
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'content': content,
                'timestamp': message['created_at'].isoformat()
            }
            
            # Emit to chat room (both users if online)
            chat_room = get_chat_room(sender_id, receiver_id)
            emit('new_message', message_data, room=chat_room)
            
            # Also emit to receiver's personal room for notifications
            receiver_room = f'user_{receiver_id}'
            emit('message_notification', message_data, room=receiver_room)
            
            # Confirm to sender
            emit('message_sent', {
                'status': 'success',
                'message_id': message['id']
            }, room=request.sid)
            
            # Create notification
            notification_service = NotificationService(connection_pool=connection_pool)
            notification_service.create_notification(
                user_id=receiver_id,
                type='new_message',
                reference_id=sender_id
            )
            
            logger.info(f"Message sent from {sender_id} to {receiver_id}")
            
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            emit('error', {'message': 'Internal server error'})
    
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle user disconnect"""
        try:
            #?
            #? Clean up Redis session
            #? redis_manager.delete_session_by_sid(request.sid)
            
            logger.info(f"Client disconnected: {request.sid}")
        except Exception as e:
            logger.error(f"❌ Error during disconnect: {e}")