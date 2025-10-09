// src/components/NotificationsPage.js
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { notificationApi } from "../utils/api";
import "./NotificationsPage.css";

const FALLBACK_AVATAR = "https://static-00.iconduck.com/assets.00/user-avatar-1024x1024-2xhpdo1n.png";

const NotificationsPage = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all"); // 'all' or 'unread'
  const navigate = useNavigate();

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const unreadOnly = filter === "unread";
      const res = await notificationApi.getNotifications(100, unreadOnly);
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

  useEffect(() => {
    fetchNotifications();
  }, [filter]);

  const handleNotificationClick = async (notif) => {
    if (!notif.is_read) {
      try {
        await notificationApi.markAsRead(notif.id);
        setNotifications(prev =>
          prev.map(n => n.id === notif.id ? { ...n, is_read: true } : n)
        );
      } catch (err) {
        console.error("Failed to mark as read:", err);
      }
    }

    if (notif.type === 'message') {
      navigate('/messages');
    } else if (notif.from_user?.username) {
      navigate(`/u/${encodeURIComponent(notif.from_user.username)}`);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationApi.markAllAsRead();
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    } catch (err) {
      console.error("Failed to mark all as read:", err);
    }
  };

  const handleDeleteNotification = async (notifId, e) => {
    e.stopPropagation();
    try {
      await notificationApi.deleteNotification(notifId);
      setNotifications(prev => prev.filter(n => n.id !== notifId));
    } catch (err) {
      console.error("Failed to delete notification:", err);
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

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div className="notifications-page">
      <div className="notifications-container">
        <div className="notifications-header">
          <h1>Notifications</h1>
          <div className="notifications-actions">
            <div className="filter-tabs">
              <button
                className={`filter-tab ${filter === "all" ? "active" : ""}`}
                onClick={() => setFilter("all")}
              >
                All
              </button>
              <button
                className={`filter-tab ${filter === "unread" ? "active" : ""}`}
                onClick={() => setFilter("unread")}
              >
                Unread {unreadCount > 0 && `(${unreadCount})`}
              </button>
            </div>
            {unreadCount > 0 && (
              <button className="mark-all-btn" onClick={handleMarkAllRead}>
                Mark all as read
              </button>
            )}
          </div>
        </div>

        <div className="notifications-content">
          {loading && (
            <div className="notifications-loading">
              <div className="spinner"></div>
              <p>Loading notifications...</p>
            </div>
          )}

          {!loading && notifications.length === 0 && (
            <div className="notifications-empty">
              <span className="empty-icon">🔔</span>
              <h2>No notifications yet</h2>
              <p>When someone likes you or views your profile, you'll see it here.</p>
            </div>
          )}

          {!loading && notifications.length > 0 && (
            <div className="notifications-list">
              {notifications.map((notif) => (
                <div
                  key={notif.id}
                  className={`notification-card ${!notif.is_read ? 'unread' : ''}`}
                  onClick={() => handleNotificationClick(notif)}
                >
                  <div className="notification-avatar">
                    <img
                      src={notif.from_user?.profile_picture || FALLBACK_AVATAR}
                      alt={notif.from_user?.username || 'User'}
                    />
                  </div>
                  <div className="notification-body">
                    <div className="notification-message">
                      <span className="notification-icon">{getNotificationIcon(notif.type)}</span>
                      <span className="notification-text">{getNotificationMessage(notif)}</span>
                    </div>
                    <div className="notification-time">{formatTime(notif.created_at)}</div>
                  </div>
                  <div className="notification-actions">
                    {!notif.is_read && <div className="unread-dot"></div>}
                    <button
                      className="delete-btn"
                      onClick={(e) => handleDeleteNotification(notif.id, e)}
                      aria-label="Delete notification"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default NotificationsPage;
