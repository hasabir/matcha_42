import React, { useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import "./ressetpassword.css";

const MIN_LEN = 8;

export default function ResetPassword() {
  const navigate = useNavigate();
  const [params] = useSearchParams();

  const tokenFromLink = params.get("token") || "";
  const usernameFromLink = (params.get("username") || "").toLowerCase();

  const [form, setForm] = useState({
    username: usernameFromLink,
    newPassword: "",
    confirm: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [msg, setMsg] = useState(null);
  const [err, setErr] = useState(null);

  const canSubmit = useMemo(() => {
    return (
      tokenFromLink &&
      form.username.trim() &&
      form.newPassword.length >= MIN_LEN &&
      form.newPassword === form.confirm
    );
  }, [form, tokenFromLink]);

  const onChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const onSubmit = async (e) => {
    e.preventDefault();
    setMsg(null);
    setErr(null);

    if (!canSubmit) {
      setErr("Please complete the form correctly.");
      return;
    }

    try {
      setSubmitting(true);
      const res = await fetch("http://localhost:5000/api/auth/reset_password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          token: tokenFromLink,
          username: form.username.trim(),
          new_password: form.newPassword,
        }),
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data?.error || "Reset failed");

      setMsg("Password set successfully. You can sign in now.");
      setTimeout(() => navigate("/signin"), 900);
    } catch (e2) {
      setErr(e2.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="rp-wrap">
      <div className="rp-card">
        <h1 className="rp-title">Set New Password</h1>

        <form className="rp-form" onSubmit={onSubmit}>
          {!usernameFromLink && (
            <>
              <label className="rp-label" htmlFor="username">Username</label>
              <input
                id="username"
                name="username"
                className="rp-input"
                placeholder="your username"
                value={form.username}
                onChange={onChange}
                autoComplete="username"
                type="text"
              />
            </>
          )}

          <label className="rp-label" htmlFor="newPassword">New Password</label>
          <input
            id="newPassword"
            name="newPassword"
            type="password"
            className="rp-input"
            placeholder="New Password"
            value={form.newPassword}
            onChange={onChange}
            autoComplete="new-password"
          />

          <label className="rp-label" htmlFor="confirm">Confirm New Password</label>
          <input
            id="confirm"
            name="confirm"
            type="password"
            className="rp-input"
            placeholder="Confirm New Password"
            value={form.confirm}
            onChange={onChange}
            autoComplete="new-password"
          />

          <p className="rp-help">
            Password must be at least 8 characters and include a mix of letters, numbers, and symbols.
          </p>

          <button className="rp-btn" disabled={!canSubmit || submitting}>
            {submitting ? "Setting…" : "Set Password"}
          </button>
        </form>

        {msg && <div className="rp-msg ok">{msg}</div>}
        {err && <div className="rp-msg err">{err}</div>}
      </div>
    </div>
  );
}
