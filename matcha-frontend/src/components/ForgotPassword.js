// src/components/ForgotPassword.js
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";   // ✅ useNavigate instead of redirect
import "./ForgotPassword.css"; 

const ForgotPassword = () => {
  const navigate = useNavigate();   // ✅ initialize navigate

  const [username, setUsername] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [msg, setMsg] = useState(null);
  const [err, setErr] = useState(null);

  const onSubmit = async (e) => {
    e.preventDefault();
    setErr(null);
    setMsg(null);

    if (!username.trim()) {
      setErr("Please enter your username.");
      return;
    }

    setSubmitting(true);
    try {
      const res = await fetch("http://localhost:5000/api/auth/forgot_password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ username: username.trim() }),
      });

      console.log("forgot = ", res.ok);
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data?.error || "Something went wrong.");
      } else {
        // ✅ redirect user to reset password page, passing username in query
        navigate(`/reset-password?username=${encodeURIComponent(username.trim())}`);
      }

      setMsg(
        "If an account exists for that username, we just sent instructions to reset your password."
      );
    } catch (e2) {
      setErr(e2.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fp-wrap">
      <div className="fp-card">
        <h1>Forgot your password?</h1>
        <p className="fp-sub">
          Enter your username and we’ll send you instructions to reset your password.
        </p>

        <form onSubmit={onSubmit} className="fp-form">
          <input
            type="text"
            className="fp-input"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
          />
          <button className="fp-btn" disabled={submitting}>
            {submitting ? "Sending…" : "Submit"}
          </button>
        </form>

        {msg && <div className="fp-msg ok">{msg}</div>}
        {err && <div className="fp-msg err">{err}</div>}

        <div className="fp-footer">
          <Link to="/signin">Remember your password? Sign in</Link>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
