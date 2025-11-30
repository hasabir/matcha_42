import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { useNotifications } from '../contexts/NotificationContext';
import { useAuth } from '../contexts/AuthContext';
import { tokenManager } from '../utils/tokenManager';
import './Notifications.css';

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { socket, socketConnected, currentUserId } = useNotifications(); // Use global socket with connected state
  const { isLoading: authLoading, isAuthenticated } = useAuth();

  // Fetch initial notifications
  useEffect(() => {
    const fetchNotifications = async () => {
      console.log('🔔 [Notifications] Fetching initial notifications...');
      
      // Wait for auth to complete
      if (authLoading) {
        console.log('⏳ [Notifications] Waiting for auth to complete...');
        return;
      }

      if (!isAuthenticated) {
        console.warn('⚠️ [Notifications] User not authenticated');
        setError('Please log in to view notifications');
        setLoading(false);
        return;
      }

      try {
        // First, try to load from localStorage for immediate display
        const cachedNotifications = localStorage.getItem('notifications');
        if (cachedNotifications) {
          try {
            const parsed = JSON.parse(cachedNotifications);
            console.log('💾 [Notifications] Loaded cached notifications:', parsed.length);
            setNotifications(parsed);
          } catch (e) {
            console.warn('⚠️ [Notifications] Failed to parse cached notifications:', e);
          }
        }

        console.log('🔑 [Notifications] Getting valid token...');
        
        // Use tokenManager to handle token refresh automatically
        const response = await tokenManager.authenticatedFetch(
          'http://localhost:5000/api/notifications/get_notifications',
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({})
          }
        );

        console.log('📡 [Notifications] Response status:', response.status);

        if (!response.ok) {
          if (response.status === 401 || response.status === 403) {
            console.error('❌ [Notifications] Unauthorized - authentication failed');
            setError('Session expired. Redirecting to login...');
            setTimeout(() => navigate('/signin'), 2000);
            return;
          }
          
          const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
          console.error('❌ [Notifications] Server error:', errorData);
          throw new Error(errorData.error || 'Failed to fetch notifications');
        }

        const data = await response.json();
        console.log('📥 [Notifications] Data received:', data);
        console.log('✅ [Notifications] Notifications loaded:', data.notifications?.length || 0);
        
        // Set notifications WITHOUT preserving old data - use fresh data from server
        const serverNotifications = data.notifications || [];
        setNotifications(serverNotifications);
        
        // Cache notifications for persistence
        try {
          localStorage.setItem('notifications', JSON.stringify(serverNotifications));
          console.log('💾 [Notifications] Cached notifications to localStorage');
        } catch (e) {
          console.warn('⚠️ [Notifications] Failed to cache notifications:', e);
        }
        console.log(`� [Notifications] Set ${serverNotifications.length} notifications from server`);
        
        setError(null);
        
      } catch (err) {
        console.error('❌ [Notifications] Error fetching notifications:', err);
        
        if (err.message === 'Authentication required') {
          setError('Please log in to view notifications');
          setTimeout(() => navigate('/signin'), 2000);
        } else {
          // On error, keep existing notifications
          console.log('💾 [Notifications] Keeping existing notifications despite error');
          setError(null);
        }
      } finally {
        setLoading(false);
        console.log('✅ [Notifications] Initial fetch complete');
      }
    };

    fetchNotifications();
  }, [navigate, authLoading, isAuthenticated]); // Only refetch when these change

  // Listen for real-time notifications via Socket.IO - use global socket
  useEffect(() => {
    console.log('🔍 [Notifications] Checking socket availability:', {
      socketExists: !!socket,
      socketConnected: socketConnected,
      currentUserId,
      authLoading,
      isAuthenticated
    });

    if (!socket) {
      console.log('⏳ [Notifications] No socket available yet, waiting...');
      return;
    }

    if (!socketConnected) {
      console.log('⏳ [Notifications] Socket not connected yet, waiting...');
      return;
    }

    if (!currentUserId) {
      console.log('⏳ [Notifications] Current user ID not available yet');
      return;
    }

    console.log('✅ [Notifications] Socket ready, setting up event listeners');
    console.log('🆔 [Notifications] Socket ID:', socket.id);
    console.log('👤 [Notifications] Current user ID:', currentUserId);

    // Join notification room
    socket.emit('join_notifications', { user_id: currentUserId });
    console.log('📡 [Notifications] Joined notification room for user:', currentUserId);

    const handleNewNotification = (data) => {
      console.log('🔔 [Notifications] NEW NOTIFICATION received:', data);
      
      // Skip message notifications - they're handled by message_notification
      if (data.type === 'new_message') {
        console.log('⚠️ [Notifications] Skipping message notification - handled by message_notification');
        return;
      }
      
      const newNotification = {
        notification_id: data.notification_id || Date.now(),
        type: data.type || data.notification?.type || 'notification',
        reference_id: data.reference_id || data.sender_id,
        message: data.message || data.content || 'New notification',
        seen: false,
        received_at: data.received_at || new Date().toISOString() // Use ISO string for consistency
      };
      
      // Check for duplicates first
      setNotifications(prev => {
        const exists = prev.some(n => 
          n.notification_id === newNotification.notification_id ||
          (n.type === newNotification.type && 
           n.reference_id === newNotification.reference_id &&
           Math.abs(new Date(n.received_at) - new Date(newNotification.received_at)) < 1000)
        );
        
        if (exists) {
          console.log('⚠️ [Notifications] Duplicate notification detected, skipping');
          return prev;
        }
        
        console.log('📝 [Notifications] Adding notification to list');
        
        const updated = [newNotification, ...prev];
        
        // Cache updated notifications
        try {
          localStorage.setItem('notifications', JSON.stringify(updated));
          console.log('💾 [Notifications] Cached updated notifications');
        } catch (e) {
          console.warn('⚠️ [Notifications] Failed to cache updated notifications:', e);
        }
        
        // Don't show toast - the Navbar popup will handle the notification display
        
        return updated;
      });
    };

    const handleMessageNotification = (data) => {
      console.log('💬 [Notifications] MESSAGE notification received:', data);
      
      const messageNotification = {
        notification_id: data.message_id || `msg-${data.sender_id}-${Date.now()}`,
        type: 'new_message',
        reference_id: data.sender_id,
        message: `New message from ${data.sender_username || 'Someone'}`,
        seen: false,
        received_at: data.timestamp || new Date().toISOString(), // Use ISO string
        sender_username: data.sender_username
      };
      
      console.log('📝 [Notifications] Prepared notification:', messageNotification);
      
      setNotifications(prev => {
        // Check if this message notification already exists (prevent duplicates)
        const exists = prev.some(n => 
          n.notification_id === messageNotification.notification_id ||
          (n.type === 'new_message' && 
           n.reference_id === data.sender_id &&
           Math.abs(new Date(n.received_at) - new Date(messageNotification.received_at)) < 2000)
        );
        
        if (exists) {
          console.log('⚠️ [Notifications] Duplicate message notification detected, skipping');
          return prev;
        }
        
        console.log('📝 [Notifications] Adding message notification to list');
        
        const updated = [messageNotification, ...prev];
        
        // Cache updated notifications
        try {
          localStorage.setItem('notifications', JSON.stringify(updated));
          console.log('💾 [Notifications] Cached updated message notifications');
        } catch (e) {
          console.warn('⚠️ [Notifications] Failed to cache updated message notifications:', e);
        }
        
        // Don't show toast - the Navbar popup will handle the notification display
        
        return updated;
      });
    };

    const handleNewMatch = (data) => {
      console.log('🎉 [Notifications] MATCH notification received:', data);
      
      const matchNotification = {
        notification_id: Date.now(),
        type: 'match',
        reference_id: data.user_id,
        message: data.message || 'You have a new match!',
        seen: false,
        received_at: new Date().toISOString()
      };
      
      setNotifications(prev => [matchNotification, ...prev]);
    };

    const handleUnliked = (data) => {
      console.log('💔 [Notifications] UNLIKED notification received:', data);
      
      const unlikeNotification = {
        notification_id: Date.now(),
        type: 'unliked',
        reference_id: data.user_id,
        message: data.message || 'Someone unliked you',
        seen: false,
        received_at: new Date().toISOString()
      };
      
      setNotifications(prev => [unlikeNotification, ...prev]);
    };

    // Attach event listeners
    socket.on('new_notification', handleNewNotification);
    socket.on('message_notification', handleMessageNotification);
    socket.on('new_match', handleNewMatch);
    socket.on('unliked', handleUnliked);

    console.log('✅ [Notifications] Event listeners attached');

    return () => {
      console.log('🧹 [Notifications] Cleaning up event listeners');
      socket.off('new_notification', handleNewNotification);
      socket.off('message_notification', handleMessageNotification);
      socket.off('new_match', handleNewMatch);
      socket.off('unliked', handleUnliked);
    };
  }, [socket, socketConnected, currentUserId, authLoading, isAuthenticated]);

  const markAsSeen = async (notificationId, notificationType) => {
    console.log('👁️ [Notifications] Marking notification as seen:', notificationId, 'type:', notificationType);
    
    // Optimistically update UI
    setNotifications(prev => {
      const updated = prev.map(notif =>
        notif.notification_id === notificationId
          ? { ...notif, seen: true }
          : notif
      );
      
      // Update cache
      try {
        localStorage.setItem('notifications', JSON.stringify(updated));
        console.log('💾 [Notifications] Updated cached notifications');
      } catch (e) {
        console.warn('⚠️ [Notifications] Failed to update cached notifications:', e);
      }
      
      return updated;
    });
    
    try {
      const response = await tokenManager.authenticatedFetch(
        'http://localhost:5000/api/notifications/mark_notification_seen',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ notification_id: notificationId }),
        }
      );

      if (response.ok) {
        console.log('✅ [Notifications] Notification marked as seen on backend');
        // Emit event to update context count with notification type
        window.dispatchEvent(new CustomEvent('notification-marked-seen', { 
          detail: { notificationId, type: notificationType } 
        }));
      } else {
        console.warn('⚠️ [Notifications] Failed to mark as seen:', response.status);
        // Revert optimistic update on failure
        setNotifications(prev =>
          prev.map(notif =>
            notif.notification_id === notificationId
              ? { ...notif, seen: false }
              : notif
          )
        );
      }
    } catch (err) {
      console.error('❌ [Notifications] Error marking notification as seen:', err);
      // Revert optimistic update on error
      setNotifications(prev =>
        prev.map(notif =>
          notif.notification_id === notificationId
            ? { ...notif, seen: false }
            : notif
        )
      );
    }
  };

  const handleNotificationClick = async (notification) => {
    console.log('🖱️ [Notifications] Notification clicked:', notification.type);
    
    // Mark as seen with notification type
    markAsSeen(notification.notification_id, notification.type);
    
    // Handle message notifications - navigate to chat with specific user
    if (notification.type === 'new_message') {
      if (notification.reference_id) {
        // Navigate to chat with userId parameter to auto-select the conversation
        navigate(`/chat?userId=${notification.reference_id}`);
      } else {
        navigate('/chat');
      }
    } 
    // Handle match notifications - also navigate to chat
    else if (notification.type === 'match') {
      if (notification.reference_id) {
        navigate(`/chat?userId=${notification.reference_id}`);
      } else {
        navigate('/chat');
      }
    } 
    // Handle other notifications - navigate to profile
    // reference_id is user_id (number), but we need username for profile route
    else if (notification.reference_id) {
      try {
        console.log('🔍 [Notifications] Fetching username for user_id:', notification.reference_id);
        
        // Fetch user details to get username
        const response = await tokenManager.authenticatedFetch(
          `http://localhost:5000/api/profile/get_user_by_id/${notification.reference_id}`
        );
        
        if (response.ok) {
          const userData = await response.json();
          const username = userData.username || userData.result?.username;
          
          if (username) {
            console.log('✅ [Notifications] Found username:', username);
            navigate(`/profile/${username}`);
          } else {
            console.error('❌ [Notifications] No username in response:', userData);
            toast.error('Could not load user profile');
          }
        } else {
          console.error('❌ [Notifications] Failed to fetch username:', response.status);
          toast.error('User not found');
        }
      } catch (err) {
        console.error('❌ [Notifications] Error fetching username:', err);
        toast.error('Failed to load profile');
      }
    }
  };

  const getNotificationIcon = (type) => {
    const icons = {
      'like': '❤️',
      'match': '🎉',
      'profile_view': '👀',
      'new_message': '💬',
      'unliked': '💔',
      'dislike': '👎',
      'block': '🚫',
      'notification': '🔔'
    };
    return icons[type] || '🔔';
  };

  const getNotificationMessage = (notification) => {
    if (notification.message) return notification.message;
    
    const messages = {
      'like': 'Someone liked your profile',
      'match': 'You have a new match!',
      'profile_view': 'Someone viewed your profile',
      'new_message': 'You have a new message',
      'unliked': 'Someone unliked you',
      'dislike': 'Someone passed on your profile',
      'block': 'Someone blocked you',
      'notification': 'New notification'
    };
    return messages[notification.type] || 'New notification';
  };

  const formatTime = (timestamp) => {
    try {
      if (!timestamp) return 'Just now';
      
      // Parse the timestamp - handle both ISO strings and Date objects
      const date = new Date(timestamp);
      
      // Check if date is valid
      if (isNaN(date.getTime())) {
        console.warn('⚠️ [Notifications] Invalid timestamp:', timestamp);
        return 'Just now';
      }
      
      const now = new Date();
      const diffMs = now.getTime() - date.getTime(); // Difference in milliseconds
      const diffSec = Math.floor(diffMs / 1000);
      
      // Log for debugging
      console.log('📅 [Notifications] Formatting time:', { 
        timestamp, 
        parsedDate: date.toISOString(), 
        now: now.toISOString(), 
        diffSec 
      });
      
      // Handle future timestamps (clock skew)
      if (diffSec < 0) {
        console.warn('⚠️ [Notifications] Future timestamp detected:', { timestamp, diffSec });
        return 'Just now';
      }
      
      // Format relative time
      if (diffSec < 10) return 'Just now';
      if (diffSec < 60) return `${diffSec}s ago`;
      if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
      if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
      if (diffSec < 604800) return `${Math.floor(diffSec / 86400)}d ago`;
      if (diffSec < 2592000) return `${Math.floor(diffSec / 604800)}w ago`;
      
      // For older notifications, show the actual date
      return date.toLocaleDateString();
    } catch (e) {
      console.error('❌ [Notifications] Error formatting time:', e, 'timestamp:', timestamp);
      return 'Recently';
    }
  };

  // Show loading while auth is initializing
  if (authLoading) {
    return (
      <div className="notifications-container">
        <h2>Notifications</h2>
        <p>Initializing...</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="notifications-container">
        <h2>Notifications</h2>
        <p>Loading notifications...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="notifications-container">
        <h2>Notifications</h2>
        <p className="error">{error}</p>
      </div>
    );
  }

  const handleClearAll = async () => {
    if (notifications.length === 0) return;
    
    const confirmed = window.confirm('Are you sure you want to clear all notifications?');
    if (!confirmed) return;
    
    try {
      console.log('🗑️ [Notifications] Clearing all notifications...');
      
      // Clear from backend database first
      const response = await tokenManager.authenticatedFetch(
        'http://localhost:5000/api/notifications/clear_all_notifications',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Failed to clear notifications from server');
      }

      console.log('✅ [Notifications] Cleared from backend database');
      
      // Clear from state and localStorage
      setNotifications([]);
      localStorage.removeItem('notifications');
      
      toast.success('All notifications cleared', {
        position: 'top-right',
        autoClose: 2000,
      });
      
      console.log('✅ [Notifications] All notifications cleared');
    } catch (err) {
      console.error('❌ [Notifications] Error clearing notifications:', err);
      toast.error('Failed to clear notifications: ' + err.message);
    }
  };

  return (
    <div className="notifications-container">
      <div className="notifications-header">
        <h2>Notifications</h2>
        {notifications.length > 0 && (
          <button 
            className="clear-all-btn" 
            onClick={handleClearAll}
            title="Clear all notifications"
          >
            🗑️ Clear All
          </button>
        )}
      </div>
      {!socket && (
        <div style={{ padding: '10px', background: '#fff3cd', borderRadius: '4px', marginBottom: '10px' }}>
          ⏳ Connecting to notification service...
        </div>
      )}
      {notifications.length === 0 ? (
        <p className="no-notifications">No notifications yet.</p>
      ) : (
        <div className="notifications-list">
          {notifications.map((notification) => (
            <div
              key={notification.notification_id}
              className={`notification-item ${notification.seen ? 'seen' : 'unseen'}`}
              onClick={() => handleNotificationClick(notification)}
            >
              <span className="notification-icon">
                {getNotificationIcon(notification.type)}
              </span>
              <div className="notification-content">
                <p className="notification-message">
                  {getNotificationMessage(notification)}
                </p>
                {/* Removed timestamp display as requested */}
              </div>
              {!notification.seen && <span className="unread-dot"></span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Notifications;