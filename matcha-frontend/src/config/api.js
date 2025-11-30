// API Configuration for MatchUp
// This file centralizes all API endpoints and Socket.IO configuration

// Use environment variables with fallbacks
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
export const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || 'http://localhost:5000';

// Socket.IO configuration
export const SOCKET_CONFIG = {
  transports: ['websocket', 'polling'],
  reconnection: true,
  reconnectionAttempts: 15, // Increased attempts
  reconnectionDelay: 1000,
  reconnectionDelayMax: 10000, // Increased max delay
  timeout: 20000, // Increased timeout
  autoConnect: false, // We'll connect manually after auth
  forceNew: true, // Force new connection
  upgrade: true, // Allow transport upgrades
  // Add ping/pong configuration
  pingTimeout: 60000, // 60 seconds
  pingInterval: 25000, // 25 seconds
  // Add connection state management
  rememberUpgrade: true,
  // Add error handling
  withCredentials: true,
};

// API endpoints
export const ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/auth/login',
    LOGOUT: '/api/auth/logout',
    REGISTER: '/api/auth/register',
  },
  CHAT: {
    GET_HISTORY: '/api/chat/get_chat_history',
    UNREAD_COUNT: '/api/chat/unread_count',
  },
  NOTIFICATIONS: {
    GET_ALL: '/api/notifications/get_notifications',
    UNREAD_COUNT: '/api/notifications/unread_count',
    MARK_SEEN: '/api/notifications/mark_notification_seen',
    MARK_ALL_SEEN: '/api/notifications/mark_all_seen',
  },
};

console.log('🔧 [API Config] Loaded configuration:', {
  API_BASE_URL,
  SOCKET_URL,
  env: process.env.NODE_ENV
});
