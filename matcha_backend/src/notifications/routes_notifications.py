from flask import jsonify, request, current_app, g
import logging
import traceback
from utils.security import auth_guard
from utils.notification_service import NotificationService
from . import notifications_bp

@notifications_bp.route("/get_notifications", methods=["POST", "GET"])
@auth_guard
def get_notifications():
    """Retrieve all notifications for the authenticated user"""
    try:
        connection_pool = current_app.config.get("CONNECTION_POOL")
        if not connection_pool:
            logging.error("❌ Connection pool not available")
            return jsonify({"error": "Database connection not available"}), 500
        
        user_id = g.user_id
        
        logging.info(f"📥 Fetching notifications for user {user_id}")
        
        notification_service = NotificationService(connection_pool)
        notifications = notification_service.get_notifications(user_id)
        
        logging.info(f"✅ Found {len(notifications)} notifications for user {user_id}")
        
        return jsonify({
            "status": "success",
            "notifications": notifications or []
        }), 200
        
    except AttributeError as e:
        logging.error(f"❌ AttributeError fetching notifications: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            "error": "User authentication failed",
            "details": str(e)
        }), 401
        
    except Exception as e:
        logging.error(f"❌ Error fetching notifications: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            "error": "Failed to fetch notifications",
            "details": str(e)
        }), 500


@notifications_bp.route("/unread-count", methods=["GET"])  # Support both URL formats
@notifications_bp.route("/unread_count", methods=["GET"])
@auth_guard
def get_unread_count():
    """Get count of unread notifications for the authenticated user"""
    try:
        connection_pool = current_app.config.get("CONNECTION_POOL")
        if not connection_pool:
            logging.error("❌ Connection pool not available")
            return jsonify({
                "error": "Database connection not available",
                "unread_count": 0
            }), 500
        
        user_id = g.user_id
        
        notification_service = NotificationService(connection_pool)
        unread_count = notification_service.get_unread_count(user_id)
        
        logging.debug(f"📊 User {user_id} has {unread_count} unread notifications")
        
        return jsonify({
            "status": "success",
            "success": True,  # Added for frontend compatibility
            "unread_count": unread_count
        }), 200
        
    except Exception as e:
        logging.error(f"❌ Error getting unread count: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            "error": "Failed to get unread count",
            "success": False,
            "unread_count": 0
        }), 500


@notifications_bp.route("/mark_notification_seen", methods=["POST"])
@auth_guard
def mark_notification_seen():
    """Mark a specific notification as seen"""
    try:
        connection_pool = current_app.config.get("CONNECTION_POOL")
        user_id = g.user_id
        
        data = request.get_json()
        notification_id = data.get("notification_id")
        
        if not notification_id:
            return jsonify({"error": "notification_id is required"}), 400
        
        notification_service = NotificationService(connection_pool)
        success = notification_service.mark_as_seen(notification_id, user_id)
        
        if success:
            # Emit updated unread count via Socket.IO
            socketio = current_app.config.get("SOCKETIO")
            if socketio:
                unread_count = notification_service.get_unread_count(user_id)
                socketio.emit("unread_count_updated", {
                    "count": unread_count
                }, room=f"user_{user_id}")
            
            return jsonify({
                "status": "success",
                "message": "Notification marked as seen"
            }), 200
        else:
            return jsonify({
                "error": "Failed to mark notification as seen"
            }), 400
            
    except Exception as e:
        logging.error(f"❌ Error marking notification as seen: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            "error": "Failed to mark notification as seen",
            "details": str(e)
        }), 500


@notifications_bp.route("/mark_all_seen", methods=["POST"])
@auth_guard
def mark_all_seen():
    """Mark all notifications as seen for the authenticated user"""
    try:
        connection_pool = current_app.config.get("CONNECTION_POOL")
        user_id = g.user_id
        
        notification_service = NotificationService(connection_pool)
        success = notification_service.mark_all_as_seen(user_id)
        
        if success:
            # Emit updated unread count via Socket.IO
            socketio = current_app.config.get("SOCKETIO")
            if socketio:
                socketio.emit("unread_count_updated", {
                    "count": 0
                }, room=f"user_{user_id}")
            
            return jsonify({
                "status": "success",
                "message": "All notifications marked as seen"
            }), 200
        else:
            return jsonify({
                "error": "Failed to mark all notifications as seen"
            }), 400
            
    except Exception as e:
        logging.error(f"❌ Error marking all notifications as seen: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            "error": "Failed to mark all notifications as seen",
            "details": str(e)
        }), 500


@notifications_bp.route("/delete_notification", methods=["POST"])
@auth_guard
def delete_notification():
    """Delete a specific notification"""
    try:
        connection_pool = current_app.config.get("CONNECTION_POOL")
        user_id = g.user_id
        
        data = request.get_json()
        notification_id = data.get("notification_id")
        
        if not notification_id:
            return jsonify({"error": "notification_id is required"}), 400
        
        notification_service = NotificationService(connection_pool)
        success = notification_service.delete_notification(notification_id, user_id)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Notification deleted"
            }), 200
        else:
            return jsonify({
                "error": "Failed to delete notification"
            }), 400
            
    except Exception as e:
        logging.error(f"❌ Error deleting notification: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            "error": "Failed to delete notification",
            "details": str(e)
        }), 500


@notifications_bp.route("/clear_all_notifications", methods=["POST", "DELETE"])
@auth_guard
def clear_all_notifications():
    """Delete all notifications for the authenticated user"""
    try:
        connection_pool = current_app.config.get("CONNECTION_POOL")
        if not connection_pool:
            logging.error("❌ Connection pool not available")
            return jsonify({"error": "Database connection not available"}), 500
        
        user_id = g.user_id
        
        logging.info(f"🗑️ Clearing all notifications for user {user_id}")
        
        notification_service = NotificationService(connection_pool)
        success = notification_service.delete_all_user_notifications(user_id)
        
        if success:
            # Emit updated unread count via Socket.IO
            socketio = current_app.config.get("SOCKETIO")
            if socketio:
                socketio.emit("unread_count_updated", {
                    "count": 0
                }, room=f"user_{user_id}")
            
            logging.info(f"✅ Successfully cleared all notifications for user {user_id}")
            return jsonify({
                "status": "success",
                "message": "All notifications cleared"
            }), 200
        else:
            logging.warning(f"⚠️ No notifications to clear for user {user_id}")
            return jsonify({
                "status": "success",
                "message": "No notifications to clear"
            }), 200
            
    except Exception as e:
        logging.error(f"❌ Error clearing all notifications: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            "error": "Failed to clear all notifications",
            "details": str(e)
        }), 500