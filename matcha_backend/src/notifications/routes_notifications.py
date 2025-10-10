import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))

import logging
from flask import Blueprint, g, render_template, request, jsonify, current_app
from database.crud.notification_crud import Notification
from utils.security import auth_guard
from utils.notification_service import NotificationService
from src.notifications import notifications_bp

# Create the blueprint
# notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/get_notifications', methods=['GET'])
# @auth_guard
def get_notifications():
    """Get user notifications"""
    try:
        user_id = 1  # From auth_guard
        # user_id = g.user_id  # From auth_guard
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        connection_pool = current_app.config["CONNECTION_POOL"]
        notification_service = NotificationService(connection_pool)
        
        notifications = notification_service.get_user_notifications(
            user_id, 
            limit, 
            offset, 
            unread_only
        )
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'count': len(notifications)
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching notifications: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@notifications_bp.route('/unread_count', methods=['GET'])
@auth_guard
def get_unread_count():
    """Get count of unread notifications"""
    try:
        user_id = g.user_id
        # user_id = 1
        connection_pool = current_app.config["CONNECTION_POOL"]
        notification_service = NotificationService(connection_pool)
        
        count = notification_service.get_unread_count(user_id)
        
        return jsonify({
            'success': True,
            'unread_count': count
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching unread count: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@notifications_bp.route('/<int:notification_id>/mark_seen', methods=['PUT'])
@auth_guard
def mark_notification_seen(notification_id):
    """Mark a specific notification as seen"""
    try:
        user_id = g.user_id
        
        connection_pool = current_app.config["CONNECTION_POOL"]
        notification_service = NotificationService(connection_pool)
        
        result = notification_service.mark_notification_seen(
            notification_id=notification_id,
            user_id=user_id  # For ownership verification
        )
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Notification marked as seen'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Notification not found or access denied'
            }), 404
            
    except Exception as e:
        logging.error(f"Error marking notification as seen: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@notifications_bp.route('/mark_all_seen', methods=['PUT'])
@auth_guard
def mark_all_notifications_seen():
    """Mark all user notifications as seen"""
    try:
        user_id = g.user_id
        
        connection_pool = current_app.config["CONNECTION_POOL"]
        notification_service = NotificationService(connection_pool)
        
        result = notification_service.mark_notification_seen(user_id=user_id)
        
        return jsonify({
            'success': True,
            'message': 'All notifications marked as seen',
            'updated_count': result
        }), 200
        
    except Exception as e:
        logging.error(f"Error marking all notifications as seen: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
# @auth_guard
def delete_notification(notification_id):
    """Delete a specific notification"""
    try:
        user_id = g.user_id
        
        connection_pool = current_app.config["CONNECTION_POOL"]
        notification_crud = Notification(connection_pool)
        
        # Verify ownership before deletion
        notifications = notification_crud.get_user_notifications(user_id, limit=1)
        user_notification_ids = [n['notification_id'] for n in notifications]
        
        if notification_id not in user_notification_ids:
            return jsonify({
                'success': False,
                'error': 'Notification not found or access denied'
            }), 404
        
        result = notification_crud.delete_notification(notification_id)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Notification deleted'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete notification'
            }), 500
            
    except Exception as e:
        logging.error(f"Error deleting notification: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500









#!----------------------------------------------------
#! to remove in production

@notifications_bp.route('/', methods=['GET'])
def chat_home():
    return render_template('test.html')


@notifications_bp.route('/test', methods=['POST'])
@auth_guard
def test_notification():
    """Create a test notification (for development only)"""
    try:
        user_id = g.user_id
        notification_type = request.json.get('type', 'test')
        reference_id = request.json.get('reference_id', None)
        
        connection_pool = current_app.config["CONNECTION_POOL"]
        notification_service = NotificationService(connection_pool)
        
        notification = notification_service.create_notification(
            user_id=user_id,
            notification_type=notification_type,
            reference_id=reference_id
        )
        from utils.socket_manager import SocketManager
        
        if notification:
            return jsonify({
                'success': True,
                'message': 'Test notification created',
                'notification': notification
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create test notification'
            }), 500
            
    except Exception as e:
        logging.error(f"Error creating test notification: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500