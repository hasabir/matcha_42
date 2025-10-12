import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./ForgotPassword.css";

export default function ForgotPassword() {
  const [username, setUsername] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [msg, setMsg] = useState(null);
  const [err, setErr] = useState(null);
  const [resetToken, setResetToken] = useState(null);
  const navigate = useNavigate();

  const onSubmit = async (e) => {
    e.preventDefault();
    setErr(null);
    setMsg(null);

    const u = username.trim();
    if (!u) {
      setErr("Please enter your username.");
      return;
    }

    setSubmitting(true);
    try {
      const res = await fetch("http://localhost:5000/api/auth/forgot_password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ username: u }),
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data?.error || "Something went wrong.");

      setMsg(
        "If an account exists for that username, we sent a password reset link to your email. Please check your inbox and click the link to reset your password."
      );
      
      // Store token for dev testing (in production, this wouldn't be returned)
      if (data.token) {
        setResetToken(data.token);
      }
      
      // Clear the form
      setUsername("");
    } catch (e2) {
      setErr(e2.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleTestReset = () => {
    // Open in current tab
    window.location.href = `http://localhost:5000/api/auth/confirm_email_reset/${resetToken}`;
    
    // Also open in new tab
    window.open(`http://localhost:5000/api/auth/confirm_email_reset/${resetToken}`, '_blank');
  };

  return (
    <div className="fp-container">
      <div className="fp-wrapper">
        {/* Decorative elements */}
        <div className="fp-decoration fp-decoration-1"></div>
        <div className="fp-decoration fp-decoration-2"></div>
        
        <div className="fp-card">
          {/* Icon */}
          <div className="fp-icon-wrapper">
            <div className="fp-icon">
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2"
              >
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
              </svg>
            </div>
          </div>

          {/* Header */}
          <div className="fp-header">
            <h1 className="fp-title">Forgot your password?</h1>
            <p className="fp-subtitle">
              No worries! Enter your username and we'll send you instructions 
              to reset your password.
            </p>
          </div>

          {/* Form */}
          <form onSubmit={onSubmit} className="fp-form">
            <div className="fp-input-group">
              <label htmlFor="username" className="fp-label">
                Username
              </label>
              <div className="fp-input-wrapper">
                <span className="fp-input-icon">
                  <svg 
                    xmlns="http://www.w3.org/2000/svg" 
                    viewBox="0 0 24 24" 
                    fill="none" 
                    stroke="currentColor" 
                    strokeWidth="2"
                  >
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                </span>
                <input
                  id="username"
                  type="text"
                  className="fp-input"
                  placeholder="Enter your username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  autoComplete="username"
                  disabled={submitting}
                />
              </div>
            </div>

            <button 
              type="submit" 
              className="fp-submit-btn" 
              disabled={submitting || !username.trim()}
            >
              {submitting ? (
                <>
                  <span className="fp-spinner"></span>
                  Sending Reset Link...
                </>
              ) : (
                <>
                  <span>Send Reset Link</span>
                  <svg 
                    xmlns="http://www.w3.org/2000/svg" 
                    viewBox="0 0 24 24" 
                    fill="none" 
                    stroke="currentColor" 
                    strokeWidth="2"
                    className="fp-btn-icon"
                  >
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                    <polyline points="12 5 19 12 12 19"></polyline>
                  </svg>
                </>
              )}
            </button>
          </form>

          {/* Messages */}
          {msg && (
            <div className="fp-message fp-message-success">
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2"
              >
                <rect x="2" y="4" width="20" height="16" rx="2"></rect>
                <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path>
              </svg>
              <div>
                <div style={{ fontWeight: "600", marginBottom: "0.5rem" }}>Check Your Email</div>
                <span>{msg}</span>
                
                {/* Development Test Button */}
                {resetToken && (
                  <button
                    onClick={handleTestReset}
                    className="fp-test-btn"
                    style={{
                      marginTop: "1rem",
                      padding: "0.5rem 1rem",
                      background: "linear-gradient(135deg, #06b6d4, #3b82f6)",
                      color: "white",
                      border: "none",
                      borderRadius: "8px",
                      cursor: "pointer",
                      fontSize: "0.875rem",
                      fontWeight: "600",
                      display: "flex",
                      alignItems: "center",
                      gap: "0.5rem",
                      width: "100%",
                      justifyContent: "center"
                    }}
                  >
                    <svg 
                      xmlns="http://www.w3.org/2000/svg" 
                      viewBox="0 0 24 24" 
                      fill="none" 
                      stroke="currentColor" 
                      strokeWidth="2"
                      style={{ width: "16px", height: "16px" }}
                    >
                      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                      <polyline points="15 3 21 3 21 9"></polyline>
                      <line x1="10" y1="14" x2="21" y2="3"></line>
                    </svg>
                    Test Reset Link (Opens in Both Tabs)
                  </button>
                )}
              </div>
            </div>
          )}
          
          {err && (
            <div className="fp-message fp-message-error">
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2"
              >
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
              </svg>
              <span>{err}</span>
            </div>
          )}

          {/* Footer */}
          <div className="fp-footer">
            <Link to="/signin" className="fp-link">
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2"
              >
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
              </svg>
              <span>Back to Sign In</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
