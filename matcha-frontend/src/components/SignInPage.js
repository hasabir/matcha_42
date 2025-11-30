// src/components/SignInPage.js
import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";  // ← import Link here
import { useAuth } from "../contexts/AuthContext";
import "./SignInPage.css";

const SignInPage = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [form, setForm] = useState({ username: "", password: "" });
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [needsVerification, setNeedsVerification] = useState(false);
  const [resendingVerification, setResendingVerification] = useState(false);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleResendVerification = async () => {
    setResendingVerification(true);
    setStatus(null);

    try {
      const res = await fetch("http://localhost:5000/api/auth/resend_verification", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: form.username,
          email: form.email || "", // You might need to ask for email
        }),
      });

      const data = await res.json();

      if (res.ok) {
        setStatus("✅ Verification email sent! Please check your inbox.");
      } else {
        setStatus(data.error || "Failed to resend verification email.");
      }
    } catch (err) {
      setStatus("Could not resend verification email. Please try again.");
    } finally {
      setResendingVerification(false);
    }
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus(null);
    setNeedsVerification(false);

    try {
      const res = await fetch("http://localhost:5000/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include", // so refresh_token cookie is saved
        body: JSON.stringify({
          username: form.username,
          password: form.password,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        // Check if it's a verification error
        if (res.status === 403 && data.verified === false) {
          setNeedsVerification(true);
          setStatus(data.message || "Please verify your email before signing in.");
        } else {
          setStatus(data.error || data.message || "Login failed");
        }
      } else {
        // Save short-lived access token for API calls
        localStorage.setItem("access_token", data.access_token);

        // Fetch user data after successful login
        try {
          const userResponse = await fetch("http://localhost:5000/api/profile/my_profile", {
            method: "GET",
            headers: {
              'Authorization': `Bearer ${data.access_token}`,
            },
            credentials: 'include',
          });

          if (userResponse.ok) {
            const userData = await userResponse.json();
            
            // 🔔 Set user in AuthContext to trigger socket connections
            login({
              id: userData.user_id,
              username: userData.username,
              email: userData.email,
              token: data.access_token,
              ...userData
            });
          } else {
            // Fallback: login with just token, AuthContext will fetch user data
            login({
              token: data.access_token
            });
          }
        } catch (userError) {
          console.error("Failed to fetch user data:", userError);
          // Fallback: login with just token, AuthContext will fetch user data
          login({
            token: data.access_token
          });
        }

        // 🔔 Notify NavBar that login state changed
        window.dispatchEvent(new Event("auth-changed"));

        setStatus("Logged in!");

        // ✅ Redirect user to the dashboard after successful login
        navigate("/dashboard");
      }
    } catch (err) {
      setStatus("Could not reach server. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signin-container">
      {/* Left side - Branding */}
      <div className="signin-brand">
        <div className="brand-content">
          <div className="brand-logo">💕</div>
          <h1 className="brand-title">Welcome Back!</h1>
          <p className="brand-subtitle">
            Continue your journey to find meaningful connections
          </p>
          <div className="brand-features">
            <div className="feature-item">
              <span className="feature-icon">✨</span>
              <span>Smart matching algorithm</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">💬</span>
              <span>Real-time messaging</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">🔒</span>
              <span>Secure and private</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right side - Form */}
      <div className="signin-form-section">
        <div className="form-header">
          <h2>Sign In</h2>
          <p>
            Don't have an account?{" "}
            <Link to="/register" className="header-link">
              Sign up
            </Link>
          </p>
        </div>

        <form className="signin-form" onSubmit={onSubmit}>
          <div className="form-group">
            <label htmlFor="username" className="form-label">
              Username
            </label>
            <input
              id="username"
              name="username"
              type="text"
              className="form-input"
              placeholder="Enter your username"
              value={form.username}
              onChange={onChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              className="form-input"
              placeholder="Enter your password"
              value={form.password}
              onChange={onChange}
              required
            />
          </div>

          <Link to="/forgot-password" className="forgot-link">
            Forgot password?
          </Link>

          {status && (
            <div className={`status-message ${status.includes("✅") || status.includes("in!") ? "success" : "error"}`}>
              {status}
            </div>
          )}

          {needsVerification && (
            <div className="verification-notice">
              <p>📧 Your email is not verified yet.</p>
              <button
                type="button"
                className="resend-btn"
                onClick={handleResendVerification}
                disabled={resendingVerification}
              >
                {resendingVerification ? "Sending..." : "Resend Verification Email"}
              </button>
            </div>
          )}

          <button type="submit" className="signin-btn" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner"></span>
                Signing in…
              </>
            ) : (
              "Sign In"
            )}
          </button>
        </form>

        <p className="terms-text">
          By signing in, you agree to our{" "}
          <a href="/terms" className="terms-link">
            Terms of Service
          </a>{" "}
          and{" "}
          <a href="/privacy" className="terms-link">
            Privacy Policy
          </a>
        </p>
      </div>
    </div>
  );
};

export default SignInPage;
