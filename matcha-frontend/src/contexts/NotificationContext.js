import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';
import { toast } from 'react-toastify';
import { useAuth } from './AuthContext';
import { tokenManager } from '../utils/tokenManager';
import { SOCKET_URL, SOCKET_CONFIG } from '../config/api';

const NotificationContext = createContext();

// Export the context itself for direct useContext usage
export { NotificationContext };

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};

export const NotificationProvider = ({ children }) => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const [socket, setSocket] = useState(null);
  const [socketConnected, setSocketConnected] = useState(false);
  const [unreadMessageCount, setUnreadMessageCount] = useState(0);
  const [unreadNotificationCount, setUnreadNotificationCount] = useState(0);
  const [onlineUsers, setOnlineUsers] = useState({});
  const [typingUsers, setTypingUsers] = useState({});
  const [currentUserId, setCurrentUserId] = useState(null);
  const socketInitializedRef = useRef(false); // Prevent duplicate initialization
  const socketRef = useRef(null); // Keep reference to socket instance

  // Initialize socket connection - ONLY when user is authenticated
  useEffect(() => {
    console.log('🔄 [NotificationContext] Socket initialization triggered');
    console.log('📊 [NotificationContext] State:', {
      isLoading,
      isAuthenticated,
      hasUser: !!user,
      hasToken: !!(user?.token),
      userId: user?.id,
      socketInitialized: socketInitializedRef.current,
      socketExists: !!socketRef.current,
      socketConnected: socketRef.current?.connected || false
    });

    // Wait for auth to finish loading
    if (isLoading) {
      console.log('⏳ [NotificationContext] Waiting for auth state to load...');
      return;
    }

    // Don't connect if not authenticated
    if (!isAuthenticated || !user || !user.id) {
      console.warn('⚠️ [NotificationContext] No authenticated user - socket connection skipped');
      
      // Clean up existing socket if user logged out
      if (socketRef.current) {
        console.log('🧹 [NotificationContext] Closing socket due to logout');
        
        // Clear connection monitor
        if (socketRef.current._connectionMonitor) {
          clearInterval(socketRef.current._connectionMonitor);
        }
        
        // Clear heartbeat interval
        if (socketRef.current._heartbeatInterval) {
          clearInterval(socketRef.current._heartbeatInterval);
        }
        
        socketRef.current.close();
        socketRef.current = null;
        setSocket(null);
        setSocketConnected(false);
        setCurrentUserId(null);
        socketInitializedRef.current = false;
        
        // Clear localStorage on logout
        try {
          localStorage.removeItem('notifications');
          console.log('🧹 [NotificationContext] Cleared cached notifications on logout');
        } catch (e) {
          console.warn('⚠️ [NotificationContext] Failed to clear cached notifications:', e);
        }
      }
      return;
    }

    // If socket already exists and is connected, don't recreate
    if (socketRef.current && socketRef.current.connected) {
      console.log('✅ [NotificationContext] Socket already connected, skipping initialization');
      return;
    }

    // Prevent duplicate initialization during the same session
    if (socketInitializedRef.current && socketRef.current) {
      console.log('🚫 [NotificationContext] Socket already initialized, skipping duplicate initialization');
      return;
    }

    // Mark as initialized
    socketInitializedRef.current = true;

    // Initialize socket connection
    const initSocket = async () => {
      console.log('🚀 [NotificationContext] initSocket() called');
      
      try {
        console.log('🔑 [NotificationContext] Attempting to get valid token...');
        
        // Get valid token (will refresh if expired)
        const token = await tokenManager.getValidToken();
        
        console.log('🔑 [NotificationContext] Token retrieval result:', {
          hasToken: !!token,
          tokenLength: token ? token.length : 0
        });
        
        if (!token) {
          console.error('❌ [NotificationContext] No valid token available for socket connection');
          console.error('❌ [NotificationContext] Token manager returned:', token);
          socketInitializedRef.current = false; // Allow retry
          return;
        }

        console.log('🔌 [NotificationContext] Initializing socket connection...');
        console.log('🔑 [NotificationContext] Token available:', token.substring(0, 20) + '...');
        console.log('👤 [NotificationContext] User ID:', user.id);
        console.log('🌐 [NotificationContext] Socket URL:', SOCKET_URL);

        const socketConfig = {
          ...SOCKET_CONFIG,
          auth: { 
            token: `Bearer ${token}`,
            user_id: user.id 
          },
          extraHeaders: {
            'Authorization': `Bearer ${token}`
          }
        };

        console.log('⚙️ [NotificationContext] Socket config:', {
          url: SOCKET_URL,
          transports: socketConfig.transports,
          reconnection: socketConfig.reconnection,
          autoConnect: socketConfig.autoConnect
        });

        const newSocket = io(SOCKET_URL, socketConfig);

        // Store in ref immediately
        socketRef.current = newSocket;

        // Set up event listeners BEFORE connecting
        newSocket.on('connect', () => {
          console.log('✅ [NotificationContext] Global socket connected successfully');
          console.log('🆔 [NotificationContext] Socket ID:', newSocket.id);
          console.log('🔗 [NotificationContext] Socket connected:', newSocket.connected);
          setSocketConnected(true);
        });

        newSocket.on('connected', (data) => {
          console.log('✅ [NotificationContext] Server acknowledged connection');
          console.log('👤 [NotificationContext] Authenticated as user ID:', data.user_id);
          setCurrentUserId(data.user_id);
        });

        newSocket.on('connect_error', (error) => {
          console.error('❌ [NotificationContext] Socket connection error:', error.message);
          console.error('🔍 [NotificationContext] Error details:', error);
          setSocketConnected(false);
        });

        newSocket.on('disconnect', (reason) => {
          console.log('🔌 [NotificationContext] Socket disconnected:', reason);
          console.log('🔌 [NotificationContext] Disconnect reason:', reason);
          setSocketConnected(false);
          
          // Don't reset initialization flag for normal disconnects
          // Only reset for server-initiated disconnects
          if (reason === 'io server disconnect') {
            console.log('🔄 [NotificationContext] Server disconnected us - will retry');
            socketInitializedRef.current = false;
          }
        });

        // Manually connect the socket AFTER setting up listeners
        console.log('🔗 [NotificationContext] Calling socket.connect()...');
        console.log('🔗 [NotificationContext] Socket URL:', SOCKET_URL);
        console.log('🔗 [NotificationContext] Socket config:', socketConfig);
        
        // Add a timeout to check connection status
        setTimeout(() => {
          console.log('🔍 [NotificationContext] Socket status after 2s:', {
            connected: newSocket.connected,
            id: newSocket.id,
            readyState: newSocket.readyState
          });
        }, 2000);

        // Add periodic connection monitoring
        const connectionMonitor = setInterval(() => {
          if (newSocket && !newSocket.connected) {
            console.log('⚠️ [NotificationContext] Socket disconnected - attempting reconnection');
            newSocket.connect();
          }
        }, 5000); // Check every 5 seconds

        // Add heartbeat to keep last_seen updated
        const heartbeatInterval = setInterval(() => {
          if (newSocket && newSocket.connected) {
            newSocket.emit('heartbeat');
            console.log('💓 [NotificationContext] Sent heartbeat');
          }
        }, 60000); // Send heartbeat every 60 seconds (1 minute)

        // Listen for heartbeat acknowledgment (optional)
        newSocket.on('heartbeat_ack', (data) => {
          console.log('💓 [NotificationContext] Heartbeat acknowledged:', data.timestamp);
        });

        // Store monitors for cleanup
        newSocket._connectionMonitor = connectionMonitor;
        newSocket._heartbeatInterval = heartbeatInterval;
        
        newSocket.connect();

        // Listen for new messages (global) - NO TOAST HERE
        newSocket.on('message_notification', (data) => {
          console.log('📬 [NotificationContext] New message notification:', data);
          
          // Increment BOTH message count AND notification count for messages
          setUnreadMessageCount(prev => {
            const newCount = prev + 1;
            console.log('📨 [NotificationContext] Unread message count updated:', newCount);
            return newCount;
          });
          
          setUnreadNotificationCount(prev => {
            const newCount = prev + 1;
            console.log('🔔 [NotificationContext] Unread notification count updated (from message):', newCount);
            return newCount;
          });
          
          // NO TOAST - let the Notifications component handle it
          // This prevents duplicate toasts
        });

        // Listen for message delivery status
        newSocket.on('message_delivered', (data) => {
          console.log('✅ Message delivered:', data.message_id);
        });

        // Listen for read receipts
        newSocket.on('messages_read', (data) => {
          console.log('✅ Messages read by:', data.reader_id);
        });

        // Listen for online/offline status
        newSocket.on('user_online', (data) => {
          console.log('🟢 User came online:', data.user_id);
          setOnlineUsers(prev => ({ ...prev, [data.user_id]: true }));
        });

        newSocket.on('user_offline', (data) => {
          console.log('⚫ User went offline:', data.user_id);
          setOnlineUsers(prev => ({ ...prev, [data.user_id]: false }));
        });

        // Listen for typing indicators
        newSocket.on('user_typing', (data) => {
          setTypingUsers(prev => ({ ...prev, [data.user_id]: data.is_typing }));
          
          // Auto-clear typing after 3 seconds
          if (data.is_typing) {
            setTimeout(() => {
              setTypingUsers(prev => ({ ...prev, [data.user_id]: false }));
            }, 3000);
          }
        });

        // Listen for general notifications (likes, views, matches, etc - NOT messages)
        newSocket.on('new_notification', (data) => {
          console.log('🔔 [NotificationContext] New notification:', data);
          
          // Skip message-type notifications (handled by message_notification event)
          if (data.type === 'new_message') {
            console.log('⚠️ [NotificationContext] Skipping new_message in new_notification handler');
            return;
          }
          
          // Increment notification count for non-message notifications
          setUnreadNotificationCount(prev => {
            const newCount = prev + 1;
            console.log('🔔 [NotificationContext] Unread notification count updated:', newCount);
            return newCount;
          });
          
          // NO TOAST HERE - let the Notifications component handle it
          // This prevents duplicate toasts
        });

        newSocket.on('unread_count', (data) => {
          setUnreadNotificationCount(data.count || 0);
        });

        newSocket.on('connect_error', (error) => {
          console.error('❌ [NotificationContext] Socket connection error:', error.message);
          console.error('🔍 [NotificationContext] Error details:', error);
          console.error('🔍 [NotificationContext] Error type:', error.type);
          console.error('🔍 [NotificationContext] Error description:', error.description);
          
          // Reset initialization flag on connection error to allow retry
          socketInitializedRef.current = false;
          setSocketConnected(false);
          
          // Show user-friendly toast notification
          toast.error('Unable to connect to notification service. Retrying...', {
            position: 'bottom-right',
            autoClose: 3000,
          });
        });

        // Handle reconnection events
        newSocket.on('reconnect', (attemptNumber) => {
          console.log('🔄 [NotificationContext] Socket reconnected after', attemptNumber, 'attempts');
          setSocketConnected(true);
        });

        newSocket.on('reconnect_attempt', (attemptNumber) => {
          console.log('🔄 [NotificationContext] Socket reconnection attempt', attemptNumber);
        });

        newSocket.on('reconnect_error', (error) => {
          console.error('❌ [NotificationContext] Socket reconnection error:', error);
        });

        newSocket.on('reconnect_failed', () => {
          console.error('❌ [NotificationContext] Socket reconnection failed');
          setSocketConnected(false);
          socketInitializedRef.current = false;
        });

        newSocket.on('error', (error) => {
          console.error('❌ [NotificationContext] Socket error:', error);
          setSocketConnected(false);
        });

        newSocket.on('disconnect', (reason) => {
          console.log('🔌 [NotificationContext] Socket disconnected:', reason);
          console.log('🔌 [NotificationContext] Disconnect details:', {
            reason,
            wasConnected: newSocket.connected
          });
          setSocketConnected(false);
          
          // Reset initialization flag to allow reconnection
          if (reason === 'io server disconnect' || reason === 'io client disconnect') {
            socketInitializedRef.current = false;
          }
        });

        // Store socket in state for components to use
        setSocket(newSocket);
        console.log('✅ [NotificationContext] Socket object stored in state and ref');

      } catch (error) {
        console.error('❌ [NotificationContext] Error initializing socket:', error);
        console.error('❌ [NotificationContext] Error stack:', error.stack);
        socketInitializedRef.current = false;
        setSocketConnected(false);
      }
    };

    initSocket();

    // Cleanup function for useEffect
    return () => {
      console.log('🧹 [NotificationContext] useEffect cleanup - resetting initialization flag');
      socketInitializedRef.current = false;
    };
  }, [isAuthenticated, isLoading, user]); // Re-run when auth state changes

  // Separate cleanup effect for socket disconnection on unmount
  useEffect(() => {
    // This effect manages the socket lifecycle
    const currentSocket = socketRef.current;
    
    return () => {
      if (currentSocket) {
        console.log('🧹 [NotificationContext] Component unmounting - closing socket connection');
        
        // Clear connection monitor
        if (currentSocket._connectionMonitor) {
          clearInterval(currentSocket._connectionMonitor);
        }
        
        // Clear heartbeat interval
        if (currentSocket._heartbeatInterval) {
          clearInterval(currentSocket._heartbeatInterval);
        }
        
        currentSocket.close();
        socketRef.current = null;
        setSocket(null);
        setSocketConnected(false);
      }
    };
  }, []); // Empty dependency - only run on mount/unmount

  // Fetch initial unread counts - only when authenticated
  useEffect(() => {
    const fetchCounts = async () => {
      console.log('📊 [NotificationContext] Fetching initial unread counts...');
      
      // Don't fetch if not authenticated
      if (!isAuthenticated || !user) {
        console.log('⚠️ [NotificationContext] Skipping count fetch - not authenticated');
        // Reset counts when not authenticated
        setUnreadMessageCount(0);
        setUnreadNotificationCount(0);
        return;
      }

      try {
        console.log('🔑 [NotificationContext] Getting valid token for count fetch...');

        // Fetch unread messages
        console.log('📬 [NotificationContext] Fetching unread message count...');
        const msgResponse = await tokenManager.authenticatedFetch(
          'http://localhost:5000/api/chat/unread_count'
        );
        
        if (msgResponse.ok) {
          const msgData = await msgResponse.json();
          const messageCount = msgData.unread_count || 0;
          setUnreadMessageCount(messageCount);
          console.log('✅ [NotificationContext] Unread messages FROM BACKEND:', messageCount);
        } else {
          console.warn('⚠️ [NotificationContext] Failed to fetch unread messages:', msgResponse.status);
          setUnreadMessageCount(0); // Reset on error
        }

        // Fetch unread notifications
        console.log('🔔 [NotificationContext] Fetching unread notification count...');
        const notifResponse = await tokenManager.authenticatedFetch(
          'http://localhost:5000/api/notifications/unread_count'
        );
        
        if (notifResponse.ok) {
          const notifData = await notifResponse.json();
          const notificationCount = notifData.unread_count || 0;
          setUnreadNotificationCount(notificationCount);
          console.log('✅ [NotificationContext] Unread notifications FROM BACKEND:', notificationCount);
        } else {
          console.warn('⚠️ [NotificationContext] Failed to fetch unread notifications:', notifResponse.status);
          setUnreadNotificationCount(0); // Reset on error
        }
      } catch (error) {
        console.error('❌ [NotificationContext] Error fetching unread counts:', error);
        // Reset counts on error to avoid stale data
        setUnreadMessageCount(0);
        setUnreadNotificationCount(0);
      }
    };

    fetchCounts();
  }, [isAuthenticated, user]);

  // Listen for notification marked as seen events from Notifications component
  useEffect(() => {
    const handleNotificationSeen = (event) => {
      console.log('👁️ [NotificationContext] Notification marked as seen event received');
      
      const detail = event.detail || {};
      const notificationType = detail.type;
      
      // Decrement notification count
      setUnreadNotificationCount(prev => {
        const newCount = Math.max(0, prev - 1);
        console.log(`📊 [NotificationContext] Notification count: ${prev} -> ${newCount}`);
        return newCount;
      });
      
      // Also decrement message count if it was a message notification
      if (notificationType === 'new_message') {
        setUnreadMessageCount(prev => {
          const newCount = Math.max(0, prev - 1);
          console.log(`📨 [NotificationContext] Message count: ${prev} -> ${newCount}`);
          return newCount;
        });
      }
    };

    window.addEventListener('notification-marked-seen', handleNotificationSeen);
    
    return () => {
      window.removeEventListener('notification-marked-seen', handleNotificationSeen);
    };
  }, []);

  // Debug function to check socket status
  const checkSocketStatus = () => {
    const status = {
      socketExists: !!socketRef.current,
      socketConnected: socketRef.current?.connected || false,
      socketId: socketRef.current?.id || null,
      currentUserId,
      isAuthenticated,
      isLoading,
      socketInitialized: socketInitializedRef.current
    };
    console.log('🔍 [NotificationContext] Socket status check:', status);
    return status;
  };

  // Function to explicitly disconnect socket (called on logout)
  const disconnectSocket = () => {
    console.log('🔌 [NotificationContext] Explicitly disconnecting socket on logout');
    
    if (socketRef.current) {
      // Emit logout event to backend before disconnecting
      if (socketRef.current.connected) {
        try {
          console.log('📤 [NotificationContext] Emitting user_logout event for user:', currentUserId);
          
          // Emit with acknowledgement callback to ensure it's received
          socketRef.current.emit('user_logout', (response) => {
            console.log('✅ [NotificationContext] Server acknowledged user_logout event:', response);
          });
          
          console.log('✅ [NotificationContext] user_logout event emitted');
          
          // Give the logout event a moment to reach the server before disconnecting
          // This ensures the server processes the logout and broadcasts offline status
          setTimeout(() => {
            console.log('⏱️ [NotificationContext] Now disconnecting socket after logout event');
            performDisconnect();
          }, 300); // Increased delay to ensure event is sent, processed, and broadcasted
          
          return; // Exit here, performDisconnect will be called after timeout
        } catch (e) {
          console.warn('⚠️ [NotificationContext] Failed to emit logout event:', e);
        }
      }
      
      // If not connected or error occurred, disconnect immediately
      performDisconnect();
    }
  };
  
  // Helper function to perform actual disconnect
  const performDisconnect = () => {
    if (!socketRef.current) return;
    
    console.log('🔌 [NotificationContext] Performing socket disconnect');
    
    // Clear connection monitor
    if (socketRef.current._connectionMonitor) {
      clearInterval(socketRef.current._connectionMonitor);
      socketRef.current._connectionMonitor = null;
    }
    
    // Clear heartbeat interval
    if (socketRef.current._heartbeatInterval) {
      clearInterval(socketRef.current._heartbeatInterval);
      socketRef.current._heartbeatInterval = null;
    }
    
    // Disconnect the socket
    socketRef.current.disconnect();
    socketRef.current = null;
    setSocket(null);
    setSocketConnected(false);
    setCurrentUserId(null);
    socketInitializedRef.current = false;
      
    console.log('✅ [NotificationContext] Socket disconnected successfully');
  };

  const value = {
    socket,
    socketConnected,
    currentUserId,
    unreadMessageCount,
    setUnreadMessageCount,
    unreadNotificationCount,
    setUnreadNotificationCount,
    onlineUsers,
    typingUsers,
    checkSocketStatus,
    disconnectSocket,
    // Helper method to decrease counts when messages are read
    decrementMessageCount: (count = 1) => {
      console.log(`📉 [NotificationContext] Decrementing message count by ${count}`);
      setUnreadMessageCount(prev => {
        const newCount = Math.max(0, prev - count);
        console.log(`📊 [NotificationContext] Message count: ${prev} -> ${newCount}`);
        return newCount;
      });
      // DO NOT decrement notification count here - messages and notifications are separate
    },
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};
