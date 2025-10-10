from utils.redis_manager import redis_manager
import time

def process_notifications(socketio, app):
    """Background worker to process queued notifications"""
    with app.app_context():
        while True:
            try:
                notifications = redis_manager.get_queued_notifications(count=10)
                
                for notification_data in notifications:
                    user_id = notification_data['user_id']
                    room = f'user_{user_id}'
                    
                    # Emit to user's room
                    socketio.emit(
                        'new_notification',
                        notification_data['notification'],
                        room=room,
                        namespace='/'
                    )
                    
                    print(f"✅ Notification sent to user {user_id}")
                    
            except Exception as e:
                print(f"❌ Error processing notifications: {e}")
            
            time.sleep(1)  # Check every second