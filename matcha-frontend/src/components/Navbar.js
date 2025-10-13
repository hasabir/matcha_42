// src/components/NavBar.js
import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { validateToken } from "../utils/authCheck";
import "./Navbar.css";

const NavBar = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [isAuthed, setIsAuthed] = useState(false); // Start with false to avoid flash
  const [authChecked, setAuthChecked] = useState(false);
  const navigate = useNavigate();

  // Keep track of auth state
  useEffect(() => {
    const updateAuth = async () => {
      const hasToken = !!localStorage.getItem("access_token");
      
      if (!hasToken) {
        setIsAuthed(false);
        setAuthChecked(true);
        return;
      }

      // Validate the token
      const isValid = await validateToken();
      setIsAuthed(isValid);
      setAuthChecked(true);
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
          <button
            className="menu-btn"
            aria-label="Toggle navigation"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            <span className="hamburger-icon" />
          </button>
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
