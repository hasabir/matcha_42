import os
import sys
import logging
from flask import Blueprint, request, jsonify, current_app, g
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
from database.crud.matching_operations_crud import Matching
from database.crud.user_crud import User
from database.crud.interactions_crud import Interactions
from utils.security import auth_guard
from src.chat import chat_bp
from database.crud.chat_crud import Chat

logger = logging.getLogger(__name__)


@chat_bp.route("/get_chat_history", methods=["POST"])
@auth_guard
def get_chat_history():
    """Get chat history between current user and another user"""
    try:
        # Validate JSON request
        requested_data = request.get_json()
        if not requested_data:
            return jsonify({"error": "Request body must be JSON"}), 400
        
        # Validate required keys
        required_keys = ['other_user']
        optional_keys = ['limit', 'offset']
        valid_keys = set(required_keys + optional_keys)
        
        # Check for missing required keys
        missing_keys = [key for key in required_keys if key not in requested_data]
        if missing_keys:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_keys)}"
            }), 400
        
        # Check for invalid keys
        invalid_keys = [key for key in requested_data.keys() if key not in valid_keys]
        if invalid_keys:
            return jsonify({
                "error": f"Invalid fields: {', '.join(invalid_keys)}"
            }), 400
        
        # Get database connection
        connection_pool = current_app.config.get("CONNECTION_POOL")
        if not connection_pool:
            logger.error("Database connection pool is not available")
            return jsonify({"error": "Service unavailable"}), 503
        
        # Validate and get other user
        other_username = requested_data.get("other_user", "").strip()
        if not other_username:
            return jsonify({"error": "other_user cannot be empty"}), 400
        
        # Prevent self-chat
        current_user_crud = User(connection_pool)
        current_user_data = current_user_crud.get_user_by_id(g.user_id)
        if current_user_data and current_user_data.get("username") == other_username:
            return jsonify({"error": "Cannot chat with yourself"}), 400
        
        user_crud = User(connection_pool)
        other_user_data = user_crud.get_user_by_username(username=other_username)
        
        if not other_user_data:
            return jsonify({"error": "User not found"}), 404
        
        other_user_id = other_user_data["id"]
        
        # Verify users are matched
        matching_crud = Matching(connection_pool)
        if not matching_crud.are_matched(g.user_id, other_user_id):
            return jsonify({"error": "You can only view chat history with matched users"}), 403
        
        # Check for blocks
        interactions_crud = Interactions(connection_pool, g.user_id, other_user_id)
        if interactions_crud.is_blocked():
            return jsonify({
                "error": "This user has blocked you",
                "blocked": True,
                "blocked_by": "other"
            }), 403
        if interactions_crud.did_i_block():
            return jsonify({
                "error": "You have blocked this user",
                "blocked": True,
                "blocked_by": "me"
            }), 403
        
        # Validate pagination parameters
        try:
            limit = int(requested_data.get('limit', 50))
            offset = int(requested_data.get('offset', 0))
            
            # Validate ranges
            if limit < 1 or limit > 100:
                return jsonify({"error": "limit must be between 1 and 100"}), 400
            if offset < 0:
                return jsonify({"error": "offset must be non-negative"}), 400
                
        except (ValueError, TypeError):
            return jsonify({"error": "limit and offset must be integers"}), 400
        
        # Fetch chat history
        chat_crud = Chat(connection_pool)
        messages = chat_crud.get_conversation(g.user_id, other_user_id, limit, offset)
        
        
        return jsonify({
            'success': True,
            'messages': messages,
            'count': len(messages),
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error fetching chat history: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'An error occurred while fetching chat history'
        }), 500


