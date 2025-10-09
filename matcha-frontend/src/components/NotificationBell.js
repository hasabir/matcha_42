// src/components/NotificationBell.js
import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { notificationApi } from "../utils/api";
import "./NotificationBell.css";

const FALLBACK_AVATAR = "https://static-00.iconduck.com/assets.00/user-avatar-1024x1024-2xhpdo1n.png";

const NotificationBell = () => {
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();

  // Fetch unread count
  const fetchUnreadCount = async () => {
    try {
      const res = await notificationApi.getUnreadCount();
      const data = await res.json();
      if (res.ok && data.unread_count !== undefined) {
        setUnreadCount(data.unread_count);
      }
    } catch (err) {
      console.error("Failed to fetch unread count:", err);
    }
  };

  // Fetch notifications when dropdown opens
  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const res = await notificationApi.getNotifications(20, false);
      const data = await res.json();
      if (res.ok && data.result) {
        setNotifications(data.result);
      }
    } catch (err) {
      console.error("Failed to fetch notifications:", err);
    } finally {
      setLoading(false);
    }
  };

  // Poll for unread count every 10 seconds (real-time requirement: max 10s delay)
  useEffect(() => {
    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, 10000);
    return () => clearInterval(interval);
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const toggleDropdown = () => {
    if (!showDropdown) {
      fetchNotifications();
    }
    setShowDropdown(!showDropdown);
  };

  const handleNotificationClick = async (notif) => {
    // Mark as read
    if (!notif.is_read) {
      try {
        await notificationApi.markAsRead(notif.id);
        setUnreadCount(prev => Math.max(0, prev - 1));
        setNotifications(prev =>
          prev.map(n => n.id === notif.id ? { ...n, is_read: true } : n)
        );
      } catch (err) {
        console.error("Failed to mark as read:", err);
      }
    }

    // Navigate based on notification type
    setShowDropdown(false);
    if (notif.type === 'message') {
      navigate('/messages');
    } else if (notif.from_user?.username) {
      navigate(`/u/${encodeURIComponent(notif.from_user.username)}`);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationApi.markAllAsRead();
      setUnreadCount(0);
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    } catch (err) {
      console.error("Failed to mark all as read:", err);
    }
  };

  const getNotificationMessage = (notif) => {
    const name = notif.from_user?.first_name || notif.from_user?.username || "Someone";
    
    switch (notif.type) {
      case 'like':
        return `${name} liked your profile`;
      case 'unlike':
        return `${name} unliked your profile`;
      case 'match':
        return `🎉 You matched with ${name}!`;
      case 'visit':
        return `${name} viewed your profile`;
      case 'message':
        return `New message from ${name}`;
      default:
        return notif.message || 'New notification';
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'like':
        return '❤️';
      case 'unlike':
        return '💔';
      case 'match':
        return '🎉';
      case 'visit':
        return '👁️';
      case 'message':
        return '💬';
      default:
        return '🔔';
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="notification-bell" ref={dropdownRef}>
      <button className="bell-button" onClick={toggleDropdown} aria-label="Notifications">
        <span className="bell-icon">🔔</span>
        {unreadCount > 0 && (
          <span className="bell-badge">{unreadCount > 99 ? '99+' : unreadCount}</span>
        )}
      </button>

      {showDropdown && (
        <div className="notification-dropdown">
          <div className="notification-header">
            <h3>Notifications</h3>
            {unreadCount > 0 && (
              <button className="mark-all-btn" onClick={handleMarkAllRead}>
                Mark all read
              </button>
            )}
          </div>

          <div className="notification-list">
            {loading && <div className="notification-loading">Loading...</div>}
            
            {!loading && notifications.length === 0 && (
              <div className="notification-empty">No notifications yet</div>
            )}

            {!loading && notifications.map((notif) => (
              <div
                key={notif.id}
                className={`notification-item ${!notif.is_read ? 'unread' : ''}`}
                onClick={() => handleNotificationClick(notif)}
              >
                <div className="notif-avatar">
                  <img
                    src={notif.from_user?.profile_picture || FALLBACK_AVATAR}
                    alt={notif.from_user?.username || 'User'}
                  />
                </div>
                <div className="notif-content">
                  <div className="notif-message">
                    <span className="notif-icon">{getNotificationIcon(notif.type)}</span>
                    {getNotificationMessage(notif)}
                  </div>
                  <div className="notif-time">{formatTime(notif.created_at)}</div>
                </div>
                {!notif.is_read && <div className="notif-dot"></div>}
              </div>
            ))}
          </div>

          {notifications.length > 0 && (
            <div className="notification-footer">
              <button onClick={() => { setShowDropdown(false); navigate('/notifications'); }}>
                View all notifications
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NotificationBell;
