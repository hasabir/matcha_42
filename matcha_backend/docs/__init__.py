"""
API Documentation Blueprint
"""
from flask import Blueprint, render_template, jsonify

docs_bp = Blueprint('docs', __name__)


@docs_bp.route('/')
def api_docs():
    """
    API documentation homepage
    """
    return jsonify({
        "message": "API Documentation",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth",
            "profile": "/api/profile",
            "search": "/api/search",
            "interactions": "/api/interactions",
            "chat": "/api/chat",
            "notifications": "/api/notifications"
        },
        "documentation": "Visit /api/docs/endpoints for detailed endpoint documentation"
    })


@docs_bp.route('/endpoints')
def endpoints_docs():
    """
    Detailed endpoint documentation
    """
    return jsonify({
        "auth": {
            "POST /api/auth/register": "Register a new user",
            "POST /api/auth/login": "Login user",
            "POST /api/auth/logout": "Logout user",
            "POST /api/auth/refresh": "Refresh access token",
            "POST /api/auth/forgot-password": "Request password reset",
            "POST /api/auth/reset-password": "Reset password with token"
        },
        "profile": {
            "GET /api/profile/me": "Get current user profile",
            "PUT /api/profile/update": "Update user profile",
            "PUT /api/profile/update_profile_picture": "Update profile picture",
            "DELETE /api/profile/update_profile_picture": "Delete profile picture",
            "POST /api/profile/upload_images": "Upload multiple images",
            "GET /api/profile/get_images/<username>": "Get user images",
            "DELETE /api/profile/delete_image/<image_id>": "Delete an image"
        },
        "search": {
            "GET /api/search": "Search for users",
            "POST /api/search/filter": "Filter users by criteria",
            "POST /api/search/sort": "Sort search results"
        },
        "interactions": {
            "POST /api/interactions/like": "Like a user",
            "DELETE /api/interactions/unlike": "Unlike a user",
            "POST /api/interactions/block": "Block a user",
            "DELETE /api/interactions/unblock": "Unblock a user",
            "POST /api/interactions/report": "Report a user",
            "GET /api/interactions/matches": "Get matched users"
        },
        "chat": {
            "GET /api/chat/messages": "Get chat messages",
            "POST /api/chat/send": "Send a message",
            "GET /api/chat/conversations": "Get all conversations"
        },
        "notifications": {
            "GET /api/notifications": "Get user notifications",
            "PUT /api/notifications/read": "Mark notifications as read",
            "DELETE /api/notifications/<notification_id>": "Delete a notification"
        }
    })


@docs_bp.route('/status')
def api_status():
    """
    API status endpoint
    """
    return jsonify({
        "status": "ok",
        "message": "API is running"
    })
