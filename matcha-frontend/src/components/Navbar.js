// src/components/NavBar.js
import React, { useEffect, useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { useNotifications } from '../contexts/NotificationContext';
import "./Navbar.css";

const NavBar = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [showNotificationPopup, setShowNotificationPopup] = useState(false);
  const [latestNotifications, setLatestNotifications] = useState([]);
  const { isAuthenticated, logout: authLogout, isLoading } = useAuth();
  const { unreadNotificationCount, disconnectSocket, socket } = useNotifications(); // Use global notification count
  const navigate = useNavigate();
  const location = useLocation();

  // Close menu when navigating to a different page
  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  // Listen for new notifications via socket and show popup
  useEffect(() => {
    if (!socket) return;

    const handleNewNotification = (data) => {
      console.log('🔔 [Navbar] New notification received:', data);
      
      // Skip message notifications - they're handled by message_notification
      if (data.type === 'new_message') {
        return;
      }
      
      const notification = {
        id: data.notification_id || Date.now(),
        type: data.type || 'notification',
        message: data.message || 'New notification',
        timestamp: new Date()
      };
      
      // Replace the entire list with just the new notification
      setLatestNotifications([notification]);
      
      // Show popup
      setShowNotificationPopup(true);
      
      // Auto-hide popup after 5 seconds and clear notifications
      setTimeout(() => {
        setShowNotificationPopup(false);
        setLatestNotifications([]);
      }, 5000);
    };

    const handleMessageNotification = (data) => {
      console.log('💬 [Navbar] Message notification received:', data);
      
      const notification = {
        id: data.message_id || `msg-${Date.now()}`,
        type: 'new_message',
        message: `New message from ${data.sender_username || 'Someone'}`,
        timestamp: new Date()
      };
      
      // Replace the entire list with just the new notification
      setLatestNotifications([notification]);
      
      // Show popup
      setShowNotificationPopup(true);
      
      // Auto-hide popup after 5 seconds and clear notifications
      setTimeout(() => {
        setShowNotificationPopup(false);
        setLatestNotifications([]);
      }, 5000);
    };

    socket.on('new_notification', handleNewNotification);
    socket.on('message_notification', handleMessageNotification);
    socket.on('new_match', handleNewNotification);
    socket.on('unliked', handleNewNotification);

    return () => {
      socket.off('new_notification', handleNewNotification);
      socket.off('message_notification', handleMessageNotification);
      socket.off('new_match', handleNewNotification);
      socket.off('unliked', handleNewNotification);
    };
  }, [socket]);

  const handleLogout = async () => {
    try {
      // Disconnect socket first to immediately update online status
      if (disconnectSocket) {
        disconnectSocket();
      }
      
      // Wait for socket disconnect to complete and broadcast offline status
      await new Promise(resolve => setTimeout(resolve, 400));
      
      const token = localStorage.getItem("access_token");
      await fetch("http://localhost:5000/api/auth/logout", {
        method: "POST",
        credentials: "include",
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      }).catch(() => {});
      
      // Use AuthContext logout to clear user state
      authLogout();
      navigate("/signin");
    } catch (e) {
      console.error("Logout error", e);
      navigate("/signin");
    }
  };

  // Define pages that show up in the authenticated user's dropdown menu.  The
  // chat page was added here so it appears alongside Discover, Profile and
  // Settings when the hamburger menu is opened.  Without this entry the chat
  // screen would only be reachable via the small chat icon in the navigation
  // bar.
  const authedPages = [
    { name: "Discover", path: "/discover" },
    { name: "Profile", path: "/profile" },
    { name: "Chat", path: "/chat" },
    { name: "Notifications", path: "/notifications" },
    { name: "Settings", path: "/settings" },
  ];

  // Don't render until we've checked auth state to prevent flash
  if (isLoading) {
    return (
      <nav className="navbar">
        <div className="nav-left">
          <Link to="/" className="nav-logo">
            <span className="nav-icon" />
            <span className="nav-brand">MatchUp</span>
          </Link>
        </div>
        <div className="nav-right">
          {/* Show minimal content while checking auth */}
        </div>
      </nav>
    );
  }

  return (
    <nav className="navbar">
      {/* Brand */}
      <div className="nav-left">
        <Link 
          to={isAuthenticated ? "/profile" : "/"} 
          className="nav-logo"
          onClick={() => setMenuOpen(false)} // Close menu when logo is clicked
        >
          <span className="nav-icon" />
          <span className="nav-brand">MatchUp</span>
        </Link>
      </div>

      {/* Right-hand controls */}
      <div className="nav-right">
        {/* Show Sign In and Sign Up buttons when NOT authenticated */}
        {!isAuthenticated && (
          <>
            <Link to="/signin" className="signup-btn">
              Sign In
            </Link>
            <Link to="/register" className="signup-btn">
              Sign Up
            </Link>
          </>
        )}
        
        {/* Show all navigation buttons when authenticated (but hide on profile-step-one) */}
        {isAuthenticated && location.pathname !== "/profile-step-one" && (
          <>
            <Link to="/discover" className="nav-btn">
              Discover
            </Link>
            <Link to="/profile" className="nav-btn">
              Profile
            </Link>
            <Link to="/chat" className="nav-btn">
              Chat
            </Link>
            <div className="notification-wrapper">
              <Link 
                to="/notifications" 
                className="notification-btn" 
                aria-label="Notifications"
                onClick={() => {
                  setMenuOpen(false);
                  setShowNotificationPopup(false);
                  // Notification count is managed in NotificationContext
                }}
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="notification-icon">
                  <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                  <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                </svg>
                {unreadNotificationCount > 0 && (
                  <span className="notification-badge">{unreadNotificationCount > 99 ? '99+' : unreadNotificationCount}</span>
                )}
              </Link>
              
              {/* Notification Popup */}
              {showNotificationPopup && latestNotifications.length > 0 && (
                <div className="notification-popup">
                  <div className="notification-popup-header">
                    <h4>Recent Notifications</h4>
                    <button 
                      className="close-popup-btn"
                      onClick={() => {
                        setShowNotificationPopup(false);
                        setLatestNotifications([]);
                      }}
                    >
                      ×
                    </button>
                  </div>
                  <div className="notification-popup-list">
                    {latestNotifications.map(notif => (
                      <div 
                        key={notif.id} 
                        className="notification-popup-item"
                        onClick={() => {
                          setShowNotificationPopup(false);
                          setLatestNotifications([]);
                          navigate(notif.type === 'new_message' ? '/chat' : '/notifications');
                        }}
                      >
                        <span className="popup-icon">
                          {notif.type === 'like' && '❤️'}
                          {notif.type === 'match' && '🎉'}
                          {notif.type === 'profile_view' && '👀'}
                          {notif.type === 'new_message' && '💬'}
                          {notif.type === 'unliked' && '💔'}
                          {!['like', 'match', 'profile_view', 'new_message', 'unliked'].includes(notif.type) && '🔔'}
                        </span>
                        <span className="popup-message">{notif.message}</span>
                      </div>
                    ))}
                  </div>
                  <div className="notification-popup-footer">
                    <Link 
                      to="/notifications" 
                      className="view-all-link"
                      onClick={() => {
                        setShowNotificationPopup(false);
                        setLatestNotifications([]);
                      }}
                    >
                      View All Notifications →
                    </Link>
                  </div>
                </div>
              )}
            </div>
            <Link to="/settings" className="nav-btn">
              Settings
            </Link>
            <button className="nav-btn logout-nav-btn" onClick={handleLogout}>
              Logout
            </button>
            {/* Chat icon - visible on mobile */}
            <Link
              to="/chat"
              className="chat-icon-btn"
              aria-label="Chat"
              onClick={() => setMenuOpen(false)}
            >
              <span role="img" aria-label="Chat" className="chat-icon-mobile">
                💬
              </span>
            </Link>
            {/* Hamburger menu button - only visible on mobile */}
            <button
              className="menu-btn"
              aria-label="Toggle navigation"
              onClick={() => setMenuOpen(!menuOpen)}
            >
              <span className="hamburger-icon" />
            </button>
          </>
        )}
      </div>

      {/* Dropdown menu for mobile */}
      {isAuthenticated && (
        <div className={`nav-menu ${menuOpen ? "open" : ""}`}>
          {authedPages.map((page) => (
            <Link
              key={page.path}
              to={page.path}
              className="nav-link"
              onClick={() => setMenuOpen(false)}
            >
              {page.name}
            </Link>
          ))}
          <button
            className="nav-link logout-btn"
            onClick={() => {
              setMenuOpen(false);
              handleLogout();
            }}
          >
            Logout
          </button>
        </div>
      )}
    </nav>
  );
};

export default NavBar;