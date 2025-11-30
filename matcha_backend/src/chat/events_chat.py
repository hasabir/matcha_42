import logging
from flask_socketio import emit, join_room, leave_room
from flask import current_app, request
import sys
import os
import jwt
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
from database.crud.interactions_crud import Interactions
from utils.security import SecurityUtils, auth_guard
from utils.notification_service import NotificationService
from utils.redis_manager import redis_manager
from utils.realtime_monitor import log_delay
from database.crud.chat_crud import Chat
from database.crud.matching_operations_crud import Matching

logger = logging.getLogger(__name__)


def get_chat_room(user_id_1, user_id_2):
    """Generate consistent chat room name for two users"""
    return f'chat_{min(user_id_1, user_id_2)}_{max(user_id_1, user_id_2)}'


def register_chat_socket_events(socketio):
    """Register all chat Socket.IO event handlers"""
    
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
                emit('error', {
                    'message': 'This user has blocked you',
                    'blocked': True,
                    'blocked_by': 'other'
                })
                return
            if interactions_crud.did_i_block():
                emit('error', {
                    'message': 'You have blocked this user',
                    'blocked': True,
                    'blocked_by': 'me'
                })
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
        """Send a message to another user with delay tracking (10-second requirement)"""
        message_start = time.time()  # Track message delivery delay
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
            if interactions_crud.is_blocked():
                emit('error', {
                    'message': 'This user has blocked you. You cannot send messages.',
                    'blocked': True,
                    'blocked_by': 'other'
                })
                return
            if interactions_crud.did_i_block():
                emit('error', {
                    'message': 'You have blocked this user. You cannot send messages.',
                    'blocked': True,
                    'blocked_by': 'me'
                })
                return
            
            # Get sender info for notification
            from database.crud.user_crud import User
            user_crud = User(connection_pool)
            sender_data = user_crud.get_user_by_id(sender_id)
            sender_username = sender_data.get('username', 'Someone') if sender_data else 'Someone'
            
            # Create message in database
            logger.info(f"💾 Attempting to create message: {sender_id} -> {receiver_id}")
            chat_crud = Chat(connection_pool=connection_pool)
            message = chat_crud.create_message(sender_id, receiver_id, content)
            
            if not message:
                logger.error(f"❌ Failed to create message in database: sender={sender_id}, receiver={receiver_id}, content_length={len(content)}")
                emit('error', {'message': 'Failed to create message'})
                return
            
            logger.info(f"✅ Message created in DB: ID={message.get('id')}")
            
            # Prepare message data - handle datetime serialization
            timestamp = message.get('created_at')
            if timestamp and hasattr(timestamp, 'isoformat'):
                timestamp = timestamp.isoformat()
            elif not isinstance(timestamp, str):
                from datetime import datetime
                timestamp = datetime.now().isoformat()
            
            message_data = {
                'message_id': message['id'],
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'content': content,
                'timestamp': timestamp,
                'sender_username': sender_username  # Include sender username
            }
            
            # Emit to chat room (both users if online)
            chat_room = get_chat_room(sender_id, receiver_id)
            socketio.emit('new_message', message_data, room=chat_room)
            logger.info(f"📨 Emitted new_message to chat room: {chat_room}")
            
            # Emit message notification to receiver's personal notification room
            receiver_room = f'user_{receiver_id}'
            socketio.emit('message_notification', message_data, room=receiver_room)
            logger.info(f"🔔 Emitted message_notification to receiver room: {receiver_room}")
            
            # Confirm to sender
            emit('message_sent', {
                'status': 'success',
                'message_id': message['id'],
                'timestamp': timestamp
            }, room=request.sid)
            logger.info(f"✅ Sent confirmation to sender (SID: {request.sid})")
            
            # Create notification for new message (this will emit via the notification worker)
            try:
                notification_service = NotificationService(connection_pool)
                notification_service.create_notification(
                    user_id=receiver_id,
                    notification_type='new_message',
                    reference_id=sender_id
                )
                logger.info(f"✅ Notification created for receiver {receiver_id}")
            except Exception as notif_error:
                logger.error(f"⚠️ Error creating notification (message still sent): {notif_error}")
            
            logger.info(f"📬 Message successfully sent from {sender_id} to {receiver_id}")
            
            # Track message delivery delay (10-second requirement)
            log_delay('chat_message', message_start, user_id=sender_id,
                     additional_info={'receiver_id': receiver_id, 'message_id': message.get('id')})
            
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}", exc_info=True)
            emit('error', {'message': 'Internal server error'})
            # Track failed message delay
            log_delay('chat_message_failed', message_start, 
                     additional_info={'error': str(e)})
    
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle user disconnect"""
        try:
            # Clean up Redis session
            # You'll need to implement a reverse lookup or store user_id in session
            logger.info(f"Client disconnected: {request.sid}")
        except Exception as e:
            logger.error(f"❌ Error during disconnect: {e}")