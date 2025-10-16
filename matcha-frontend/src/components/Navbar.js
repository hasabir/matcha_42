// src/components/NavBar.js
import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { validateToken } from "../utils/authCheck";
import "./Navbar.css";

const NavBar = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [isAuthed, setIsAuthed] = useState(false); // Start with false to avoid flash
  const [authChecked, setAuthChecked] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const navigate = useNavigate();

  // Keep track of auth state
  useEffect(() => {
    const updateAuth = async () => {
      const hasToken = !!localStorage.getItem("access_token");
      
      if (!hasToken) {
        setIsAuthed(false);
        setAuthChecked(true);
        setUnreadCount(0);
        return;
      }

      // Validate the token
      const isValid = await validateToken();
      setIsAuthed(isValid);
      setAuthChecked(true);
      
      // Fetch unread notifications count if authenticated
      if (isValid) {
        fetchUnreadCount();
      }
    };
    
    // Initial check
    updateAuth();
    
    // Listen for auth changes
    const handleAuthChange = () => {
      updateAuth();
    };
    
    window.addEventListener("auth-changed", handleAuthChange);
    return () => window.removeEventListener("auth-changed", handleAuthChange);
  }, []);

  // Fetch unread notifications count
  const fetchUnreadCount = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch("http://localhost:5000/api/notifications/unread_count", {
        method: "GET",
        credentials: "include",
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setUnreadCount(data.unread_count || 0);
      }
    } catch (error) {
      console.error("Failed to fetch unread count:", error);
    }
  };

  // Poll for new notifications every 30 seconds when authenticated
  useEffect(() => {
    if (!isAuthed) return;
    
    const interval = setInterval(fetchUnreadCount, 30000); // 30 seconds
    return () => clearInterval(interval);
  }, [isAuthed]);

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem("access_token");
      await fetch("http://localhost:5000/api/auth/logout", {
        method: "POST",
        credentials: "include",
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      }).catch(() => {});
      localStorage.removeItem("access_token");
      window.dispatchEvent(new Event("auth-changed"));
      navigate("/signin");
    } catch (e) {
      console.error("Logout error", e);
      navigate("/signin");
    }
  };

  const authedPages = [
    { name: "Discover", path: "/discover" },
    { name: "Profile", path: "/profile" },
    { name: "Settings", path: "/settings" },
  ];

  // Don't render until we've checked auth state to prevent flash
  if (!authChecked) {
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
          to={isAuthed ? "/profile" : "/"} 
          className="nav-logo"
          onClick={() => setMenuOpen(false)} // Close menu when logo is clicked
        >
          <span className="nav-icon" />
          <span className="nav-brand">MatchUp</span>
        </Link>
      </div>

      {/* Right-hand controls */}
      <div className="nav-right">
        {!isAuthed && (
          <>
            <Link to="/signin" className="signup-btn">
              Sign In
            </Link>
            <Link to="/register" className="signup-btn">
              Sign Up
            </Link>
          </>
        )}
        {isAuthed && (
          <>
            <Link 
              to="/notifications" 
              className="notification-btn" 
              aria-label="Notifications"
              onClick={() => {
                setMenuOpen(false);
                setUnreadCount(0); // Reset count when clicking notifications
              }}
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="notification-icon">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
              </svg>
              {unreadCount > 0 && (
                <span className="notification-badge">{unreadCount > 99 ? '99+' : unreadCount}</span>
              )}
            </Link>
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

      {/* Dropdown menu only for authed users */}
      {isAuthed && (
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
