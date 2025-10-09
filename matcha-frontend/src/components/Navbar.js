// src/components/NavBar.js
import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import NotificationBell from "./NotificationBell";
import "./Navbar.css";

const NavBar = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [isAuthed, setIsAuthed] = useState(!!localStorage.getItem("access_token"));
  const navigate = useNavigate();

  // Keep track of auth state
  useEffect(() => {
    const updateAuth = () => setIsAuthed(!!localStorage.getItem("access_token"));
    window.addEventListener("auth-changed", updateAuth);
    return () => window.removeEventListener("auth-changed", updateAuth);
  }, []);

  const handleLogout = async () => {
    try {
      await fetch("http://localhost:5000/api/auth/logout", {
        method: "POST",
        credentials: "include",
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
    { name: "Home", path: "/", icon: "🏠" },
    { name: "Discover", path: "/discover", icon: "🔍" },
    { name: "Messages", path: "/messages", icon: "💬" },
    { name: "Dashboard", path: "/dashboard", icon: "📊" },
    { name: "Settings", path: "/settings", icon: "⚙️" },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Brand */}
        <div className="nav-left">
          <Link to="/" className="nav-logo">
            <span className="nav-icon">💕</span>
            <span className="nav-brand">Matcha</span>
          </Link>
        </div>

        {/* Desktop Navigation - Only for authenticated users */}
        {isAuthed && (
          <div className="nav-center desktop-only">
            {authedPages.map((page) => (
              <Link
                key={page.path}
                to={page.path}
                className="nav-link-desktop"
              >
                <span className="nav-link-icon">{page.icon}</span>
                <span className="nav-link-text">{page.name}</span>
              </Link>
            ))}
          </div>
        )}

        {/* Right-hand controls */}
        <div className="nav-right">
          {!isAuthed ? (
            <>
              <Link to="/signin" className="btn-signin">
                Sign In
              </Link>
              <Link to="/register" className="btn-signup">
                Sign Up
              </Link>
            </>
          ) : (
            <>
              <NotificationBell />
              
              {/* Desktop Logout */}
              <button className="btn-logout desktop-only" onClick={handleLogout}>
                Logout
              </button>

              {/* Mobile Burger Menu */}
              <button
                className={`burger-btn mobile-only ${menuOpen ? "active" : ""}`}
                aria-label="Toggle navigation"
                onClick={() => setMenuOpen(!menuOpen)}
              >
                <span className="burger-line"></span>
                <span className="burger-line"></span>
                <span className="burger-line"></span>
              </button>
            </>
          )}
        </div>

        {/* Mobile Menu Overlay */}
        {isAuthed && menuOpen && (
          <div className="mobile-overlay" onClick={() => setMenuOpen(false)} />
        )}

        {/* Mobile Menu Drawer */}
        {isAuthed && (
          <div className={`mobile-menu ${menuOpen ? "open" : ""}`}>
            <div className="mobile-menu-header">
              <span className="mobile-menu-title">Navigation</span>
              <button
                className="close-btn"
                onClick={() => setMenuOpen(false)}
                aria-label="Close menu"
              >
                ✕
              </button>
            </div>
            <div className="mobile-menu-links">
              {authedPages.map((page) => (
                <Link
                  key={page.path}
                  to={page.path}
                  className="mobile-nav-link"
                  onClick={() => setMenuOpen(false)}
                >
                  <span className="mobile-link-icon">{page.icon}</span>
                  <span className="mobile-link-text">{page.name}</span>
                </Link>
              ))}
              <button
                className="mobile-logout-btn"
                onClick={() => {
                  setMenuOpen(false);
                  handleLogout();
                }}
              >
                <span className="mobile-link-icon">🚪</span>
                <span className="mobile-link-text">Logout</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default NavBar;
