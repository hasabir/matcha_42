"""
Chat routes for the Matcha dating app.
Handles real-time messaging between matched users.
"""
import logging
from flask import request, jsonify, current_app, g
from src.chat import chat_bp
from utils.security import auth_guard
from database.crud.chat_crud import Chat
from database.crud.user_crud import User
from database.crud.interactions_crud import Interactions
from database.crud.notification_crud import Notification

logger = logging.getLogger(__name__)


@chat_bp.route("/conversations", methods=["GET"])
@auth_guard
def get_conversations():
    """
    Get all conversations for the logged-in user.
    Returns list with last message, unread count, and other user info.
    """
    try:
        pool = current_app.config.get("CONNECTION_POOL")
        if not pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        chat_crud = Chat(pool)
        user_crud = User(pool)
        
        conversations = chat_crud.get_user_conversations(g.user_id)
        
        # Enrich with other user's details
        for conv in conversations:
            other_user = user_crud.get_user_by_id(conv["other_user_id"])
            if other_user:
                conv["other_username"] = other_user.get("username")
                conv["other_first_name"] = other_user.get("first_name")
                conv["other_last_name"] = other_user.get("last_name")
                conv["other_active"] = other_user.get("active", False)
        
        return jsonify({"status": "ok", "result": conversations}), 200
        
    except Exception as e:
        logger.exception("Error getting conversations")
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/conversation/<username>", methods=["GET", "POST"])
@auth_guard
def manage_conversation(username):
    """
    GET: Get or create a conversation with a specific user and return messages.
    POST: Send a message to the user (body: {message: "text"})
    
    Only works if both users are matched.
    """
    try:
        pool = current_app.config.get("CONNECTION_POOL")
        if not pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        user_crud = User(pool)
        other_user = user_crud.get_user_by_username(username)
        
        if not other_user:
            return jsonify({"error": "User not found"}), 404
        
        other_user_id = other_user["id"]
        
        # Check if users are matched
        interactions = Interactions(pool, g.user_id, other_user_id)
        if not interactions.is_matched():
            return jsonify({"error": "You can only chat with matched users"}), 403
        
        chat_crud = Chat(pool)
        conversation_id = chat_crud.get_or_create_conversation(g.user_id, other_user_id)
        
        if not conversation_id:
            return jsonify({"error": "Failed to create conversation"}), 500
        
        if request.method == "GET":
            # Get messages
            messages = chat_crud.get_conversation_messages(conversation_id)
            # Mark messages as read
            chat_crud.mark_messages_as_read(conversation_id, g.user_id)
            
            return jsonify({
                "status": "ok",
                "conversation_id": conversation_id,
                "messages": messages,
                "other_user": {
                    "id": other_user_id,
                    "username": other_user.get("username"),
                    "first_name": other_user.get("first_name"),
                    "last_name": other_user.get("last_name"),
                    "active": other_user.get("active", False)
                }
            }), 200
        
        elif request.method == "POST":
            # Send message
            data = request.get_json(force=True) or {}
            message_text = data.get("message", "").strip()
            
            if not message_text:
                return jsonify({"error": "Message cannot be empty"}), 400
            
            message = chat_crud.send_message(conversation_id, g.user_id, message_text)
            
            if not message:
                return jsonify({"error": "Failed to send message"}), 500
            
            # TODO: Emit WebSocket event for real-time delivery
            # socketio.emit('new_message', message, room=f'user_{other_user_id}')
            
            return jsonify({"status": "ok", "result": message}), 201
    
    except Exception as e:
        logger.exception("Error managing conversation")
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/messages/<int:conversation_id>", methods=["GET"])
@auth_guard
def get_messages(conversation_id):
    """
    Get messages from a specific conversation.
    Query params: limit (default 100), offset (default 0)
    """
    try:
        pool = current_app.config.get("CONNECTION_POOL")
        if not pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        chat_crud = Chat(pool)
        
        # Verify user is part of this conversation
        if not chat_crud.user_in_conversation(conversation_id, g.user_id):
            return jsonify({"error": "You are not part of this conversation"}), 403
        
        limit = request.args.get("limit", 100, type=int)
        offset = request.args.get("offset", 0, type=int)
        
        messages = chat_crud.get_conversation_messages(conversation_id, limit, offset)
        
        # Mark as read
        chat_crud.mark_messages_as_read(conversation_id, g.user_id)
        
        return jsonify({"status": "ok", "result": messages}), 200
        
    except Exception as e:
        logger.exception("Error getting messages")
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/send", methods=["POST"])
@auth_guard
def send_message():
    """
    Send a message to a conversation.
    Body: {conversation_id: int, message: "text"}
    """
    try:
        pool = current_app.config.get("CONNECTION_POOL")
        if not pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        data = request.get_json(force=True) or {}
        conversation_id = data.get("conversation_id")
        message_text = data.get("message", "").strip()
        
        if not conversation_id:
            return jsonify({"error": "conversation_id is required"}), 400
        
        if not message_text:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        chat_crud = Chat(pool)
        
        # Verify user is part of this conversation
        if not chat_crud.user_in_conversation(conversation_id, g.user_id):
            return jsonify({"error": "You are not part of this conversation"}), 403
        
        message = chat_crud.send_message(conversation_id, g.user_id, message_text)
        
        if not message:
            return jsonify({"error": "Failed to send message"}), 500
        
        # Get other user in conversation for notification
        conv_query = """
            SELECT user1_id, user2_id FROM conversations 
            WHERE id = %s
        """
        from database.dbmanager import DBManager
        db_manager = DBManager(pool)
        conv_data = db_manager.execute_query(conv_query, (conversation_id,), fetch=True)
        
        if conv_data:
            other_user_id = conv_data[0]['user2_id'] if conv_data[0]['user1_id'] == g.user_id else conv_data[0]['user1_id']
            
            # Create message notification
            notification_crud = Notification(pool)
            user_crud = User(pool)
            my_username = user_crud.get_user_by('id', g.user_id, 'username')
            
            notification_crud.create_notification(
                user_id=other_user_id,
                type='message',
                from_user_id=g.user_id,
                message=f"New message from {my_username}"
            )
        
        # TODO: Emit WebSocket event for real-time delivery
        
        return jsonify({"status": "ok", "result": message}), 201
        
    except Exception as e:
        logger.exception("Error sending message")
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/unread_count", methods=["GET"])
@auth_guard
def get_unread_count():
    """Get total unread message count for the logged-in user."""
    try:
        pool = current_app.config.get("CONNECTION_POOL")
        if not pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        chat_crud = Chat(pool)
        count = chat_crud.get_unread_message_count(g.user_id)
        
        return jsonify({"status": "ok", "unread_count": count}), 200
        
    except Exception as e:
        logger.exception("Error getting unread count")
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/mark_read/<int:conversation_id>", methods=["POST"])
@auth_guard
def mark_read(conversation_id):
    """Mark all messages in a conversation as read."""
    try:
        pool = current_app.config.get("CONNECTION_POOL")
        if not pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        chat_crud = Chat(pool)
        
        # Verify user is part of this conversation
        if not chat_crud.user_in_conversation(conversation_id, g.user_id):
            return jsonify({"error": "You are not part of this conversation"}), 403
        
        success = chat_crud.mark_messages_as_read(conversation_id, g.user_id)
        
        if success:
            return jsonify({"status": "ok"}), 200
        else:
            return jsonify({"error": "Failed to mark messages as read"}), 500
        
    except Exception as e:
        logger.exception("Error marking messages as read")
        return jsonify({"error": str(e)}), 500
