import React, { useState } from "react";
import { Link } from "react-router-dom";
import "./ForgotPassword.css";

export default function ForgotPassword() {
  const [username, setUsername] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [msg, setMsg] = useState(null);
  const [err, setErr] = useState(null);

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
        "If an account exists for that username, we sent instructions to reset your password."
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
          Enter your username and we’ll send you a reset link.
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
}
