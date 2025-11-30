from utils.redis_manager import redis_manager
from utils.realtime_monitor import log_delay
from datetime import datetime, timezone
import time

def process_notifications(socketio, app):
    """Background worker to process queued notifications with delay tracking"""
    with app.app_context():
        while True:
            try:
                notifications = redis_manager.get_queued_notifications(count=10)
                
                for notification_data in notifications:
                    notification_start = time.time()  # Track notification delivery delay
                    
                    user_id = notification_data['user_id']
                    room = f'user_{user_id}'
                    notification = notification_data['notification']
                    
                    # Get notification creation time for accurate delay measurement
                    received_at = notification.get('received_at')
                    if received_at:
                        try:
                            # Parse ISO format timestamp
                            if isinstance(received_at, str):
                                notification_created = datetime.fromisoformat(received_at.replace('Z', '+00:00'))
                                notification_start = notification_created.timestamp()
                        except:
                            pass  # Use current time if parsing fails
                    
                    # Emit to user's room with proper data structure
                    socketio.emit(
                        'new_notification',
                        {
                            'notification_id': notification.get('notification_id'),
                            'type': notification.get('type'),
                            'reference_id': notification.get('reference_id'),
                            'seen': notification.get('seen', False),
                            'received_at': notification.get('received_at'),
                            'message': get_notification_message(notification.get('type'), notification.get('reference_id'))
                        },
                        room=room,
                        namespace='/'
                    )
                    
                    # Track notification delivery delay (10-second requirement)
                    log_delay('notification_delivery', notification_start, user_id=user_id,
                             additional_info={'type': notification.get('type')})
                    
                    print(f"✅ Notification sent to user {user_id}: {notification.get('type')}")
                    
            except Exception as e:
                print(f"❌ Error processing notifications: {e}")
            
            time.sleep(1)  # Check every second

def get_notification_message(notification_type, reference_id):
    """Get user-friendly message for notification type"""
    messages = {
        'like': '❤️ Someone liked you!',
        'profile_view': '👀 Someone viewed your profile!',
        'match': '🎉 You have a new match!',
        'unliked': '💔 Someone unliked you',
        'new_message': '💬 You have a new message!',
        'block': '🚫 Someone blocked you'
    }
    return messages.get(notification_type, '🔔 New notification')