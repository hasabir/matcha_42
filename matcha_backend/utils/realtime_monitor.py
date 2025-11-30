"""
Real-time Delay Monitor
Tracks and logs delays for Socket.IO events (chat, notifications, user status)
Ensures compliance with subject requirement: "maximum delay of 10 seconds"
"""
import logging
import time
from datetime import datetime, timezone
from functools import wraps

logger = logging.getLogger(__name__)

# Delay thresholds (in seconds)
MAX_ALLOWED_DELAY = 10.0  # Subject requirement: max 10 seconds
WARNING_THRESHOLD = 5.0   # Warn if approaching the limit

class RealtimeMonitor:
    """Monitor and track delays in real-time features"""
    
    def __init__(self):
        self.delays = []
        self.violations = []
        self.warnings = []
    
    def track_event(self, event_type, start_time, end_time, user_id=None, additional_info=None):
        """
        Track a real-time event and log if it exceeds thresholds
        
        Args:
            event_type: Type of event (e.g., 'chat_message', 'notification', 'user_status')
            start_time: Timestamp when event was initiated (unix timestamp or datetime)
            end_time: Timestamp when event was completed (unix timestamp or datetime)
            user_id: Optional user ID for tracking
            additional_info: Optional dict with additional context
        """
        # Convert to timestamps if needed
        if isinstance(start_time, datetime):
            start_time = start_time.timestamp()
        if isinstance(end_time, datetime):
            end_time = end_time.timestamp()
        
        delay = end_time - start_time
        
        event_data = {
            'event_type': event_type,
            'delay': delay,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'user_id': user_id,
            'additional_info': additional_info or {}
        }
        
        self.delays.append(event_data)
        
        # Check for violations and warnings
        if delay > MAX_ALLOWED_DELAY:
            self.violations.append(event_data)
            logger.error(
                f"🚨 DELAY VIOLATION: {event_type} took {delay:.2f}s (> {MAX_ALLOWED_DELAY}s) "
                f"for user {user_id} | {additional_info or ''}"
            )
        elif delay > WARNING_THRESHOLD:
            self.warnings.append(event_data)
            logger.warning(
                f"⚠️ DELAY WARNING: {event_type} took {delay:.2f}s (approaching {MAX_ALLOWED_DELAY}s limit) "
                f"for user {user_id} | {additional_info or ''}"
            )
        else:
            logger.info(
                f"✅ {event_type} completed in {delay:.2f}s for user {user_id}"
            )
        
        return delay
    
    def get_statistics(self):
        """Get statistics about tracked delays"""
        if not self.delays:
            return {
                'total_events': 0,
                'violations': 0,
                'warnings': 0,
                'avg_delay': 0,
                'max_delay': 0
            }
        
        delay_values = [d['delay'] for d in self.delays]
        
        return {
            'total_events': len(self.delays),
            'violations': len(self.violations),
            'warnings': len(self.warnings),
            'avg_delay': sum(delay_values) / len(delay_values),
            'max_delay': max(delay_values),
            'min_delay': min(delay_values)
        }
    
    def reset_statistics(self):
        """Reset all tracked statistics"""
        self.delays = []
        self.violations = []
        self.warnings = []
        logger.info("📊 Real-time monitor statistics reset")


# Global monitor instance
realtime_monitor = RealtimeMonitor()


def monitor_delay(event_type):
    """
    Decorator to monitor delays for functions/handlers
    
    Usage:
        @monitor_delay('chat_message')
        def send_message(user_id, message):
            # Your code here
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                
                # Try to extract user_id from kwargs or args
                user_id = kwargs.get('user_id') or kwargs.get('sender_id')
                if not user_id and args:
                    # Try to find user_id in args
                    for arg in args:
                        if isinstance(arg, (int, str)) and str(arg).isdigit():
                            user_id = arg
                            break
                
                realtime_monitor.track_event(
                    event_type=event_type,
                    start_time=start_time,
                    end_time=end_time,
                    user_id=user_id,
                    additional_info={'function': func.__name__}
                )
                
                return result
            
            except Exception as e:
                end_time = time.time()
                logger.error(f"❌ Error in {event_type} (took {end_time - start_time:.2f}s): {e}")
                raise
        
        return wrapper
    return decorator


def log_delay(event_type, start_time, user_id=None, additional_info=None):
    """
    Standalone function to log a delay measurement
    
    Usage:
        start = time.time()
        # ... do work ...
        log_delay('notification_delivery', start, user_id=123)
    """
    end_time = time.time()
    return realtime_monitor.track_event(
        event_type=event_type,
        start_time=start_time,
        end_time=end_time,
        user_id=user_id,
        additional_info=additional_info
    )


def get_monitor_stats():
    """Get current monitoring statistics"""
    return realtime_monitor.get_statistics()


def reset_monitor_stats():
    """Reset monitoring statistics"""
    realtime_monitor.reset_statistics()
