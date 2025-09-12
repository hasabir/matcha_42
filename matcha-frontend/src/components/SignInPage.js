// src/components/SignInPage.js
import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";  // ← import Link here
import "./SignInPage.css";

const SignInPage = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus(null);

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
        setStatus(data.error || data.message || "Login failed");
      } else {
        // Save short-lived access token for API calls
        localStorage.setItem("access_token", data.access_token);

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
      <div className="form-wrapper">
        <h1>Welcome back</h1>

        <form className="signin-form" onSubmit={onSubmit}>
          <label htmlFor="username">Username</label>
          <input
            id="username"
            name="username"
            type="text"
            placeholder="Enter your username"
            value={form.username}
            onChange={onChange}
            required
          />

          <label htmlFor="password">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            placeholder="Enter your password"
            value={form.password}
            onChange={onChange}
            required
          />

          {/* 🔗 Go to ForgotPassword page */}
          <Link to="/forgot-password" className="forgot-link">
            Forgot password?
          </Link>

          <button type="submit" className="signin-btn" disabled={loading}>
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        {status && <p className="status">{status}</p>}

        <p className="signup-link">
          Don't have an account? <Link to="/register">Sign up</Link>
        </p>
      </div>
    </div>
  );
};

export default SignInPage;
