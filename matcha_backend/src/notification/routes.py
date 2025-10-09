# src/notification/routes.py
import logging
from flask import request, jsonify, current_app, g
from src.notification import notification_bp
from utils.security import auth_guard
from database.crud.notification_crud import Notification

logger = logging.getLogger(__name__)


@notification_bp.route("/get_notifications", methods=["GET"])
@auth_guard
def get_notifications():
    """
    Get notifications for the logged-in user.
    Query params:
        - limit: Max number of notifications (default 50)
        - unread_only: Boolean, return only unread notifications
    """
    try:
        pool = current_app.config.get("CONNECTION_POOL")
        if not pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        limit = request.args.get("limit", 50, type=int)
        unread_only = request.args.get("unread_only", "false").lower() == "true"

        notification_crud = Notification(pool)
        notifications = notification_crud.get_user_notifications(
            g.user_id, 
            limit=limit, 
            unread_only=unread_only
        )

        # Format the response
        formatted = []
        for notif in notifications:
            formatted.append({
                "id": notif.get("id"),
                "type": notif.get("type"),
                "message": notif.get("message"),
                "is_read": notif.get("is_read"),
                "created_at": notif.get("created_at").isoformat() if notif.get("created_at") else None,
                "from_user": {
                    "username": notif.get("from_username"),
                    "first_name": notif.get("first_name"),
                    "last_name": notif.get("last_name"),
                    "profile_picture": notif.get("profile_picture")
                }
            })

        return jsonify({"result": formatted}), 200

    except Exception as e:
        logger.exception("Error getting notifications")
        return jsonify({"error": str(e)}), 500


@notification_bp.route("/unread_count", methods=["GET"])
@auth_guard
def get_unread_count():
    """Get count of unread notifications."""
    try:
        pool = current_app.config.get("CONNECTION_POOL")
        if not pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        notification_crud = Notification(pool)
        count = notification_crud.get_unread_count(g.user_id)

        return jsonify({"unread_count": count}), 200

    except Exception as e:
        logger.exception("Error getting unread count")
        return jsonify({"error": str(e)}), 500


@notification_bp.route("/mark_read/<int:notification_id>", methods=["POST"])
@auth_guard
def mark_notification_read(notification_id):
    """Mark a specific notification as read."""
    try:
        pool = current_app.config.get("CONNECTION_POOL")
        if not pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        notification_crud = Notification(pool)
        success = notification_crud.mark_as_read(notification_id, g.user_id)

        if success:
            return jsonify({"status": "ok", "message": "Notification marked as read"}), 200
        else:
            return jsonify({"error": "Notification not found or already read"}), 404

    except Exception as e:
        logger.exception("Error marking notification as read")
        return jsonify({"error": str(e)}), 500


@notification_bp.route("/mark_all_read", methods=["POST"])
@auth_guard
def mark_all_read():
    """Mark all notifications as read."""
    try:
        pool = current_app.config.get("CONNECTION_POOL")
        if not pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        notification_crud = Notification(pool)
        notification_crud.mark_all_as_read(g.user_id)

        return jsonify({"status": "ok", "message": "All notifications marked as read"}), 200

    except Exception as e:
        logger.exception("Error marking all notifications as read")
        return jsonify({"error": str(e)}), 500


@notification_bp.route("/delete/<int:notification_id>", methods=["DELETE"])
@auth_guard
def delete_notification(notification_id):
    """Delete a notification."""
    try:
        pool = current_app.config.get("CONNECTION_POOL")
        if not pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        notification_crud = Notification(pool)
        success = notification_crud.delete_notification(notification_id, g.user_id)

        if success:
            return jsonify({"status": "ok", "message": "Notification deleted"}), 200
        else:
            return jsonify({"error": "Notification not found"}), 404

    except Exception as e:
        logger.exception("Error deleting notification")
        return jsonify({"error": str(e)}), 500
