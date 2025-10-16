import React, { useMemo, useState } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import "./ressetpassword.css";

const MIN_LEN = 8;

export default function ResetPassword() {
  const navigate = useNavigate();
  const [params] = useSearchParams();

  const tokenFromLink = params.get("token") || "";
  const usernameFromLink = (params.get("username") || "");

  const [form, setForm] = useState({
    username: usernameFromLink,
    newPassword: "",
    confirm: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [msg, setMsg] = useState(null);
  const [err, setErr] = useState(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  // Show error if token or username is missing
  const missingParams = !tokenFromLink || !usernameFromLink;

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

  const passwordStrength = useMemo(() => {
    const pwd = form.newPassword;
    if (!pwd) return { level: 0, text: "", color: "" };
    
    let strength = 0;
    if (pwd.length >= 8) strength++;
    if (pwd.length >= 12) strength++;
    if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) strength++;
    if (/\d/.test(pwd)) strength++;
    if (/[^A-Za-z0-9]/.test(pwd)) strength++;

    if (strength <= 2) return { level: 1, text: "Weak", color: "#ef4444" };
    if (strength <= 3) return { level: 2, text: "Fair", color: "#f59e0b" };
    if (strength <= 4) return { level: 3, text: "Good", color: "#10b981" };
    return { level: 4, text: "Strong", color: "#10b981" };
  }, [form.newPassword]);

  return (
    <div className="rp-container">
      {/* Animated background */}
      <div className="rp-bg-decoration rp-bg-decoration-1"></div>
      <div className="rp-bg-decoration rp-bg-decoration-2"></div>
      <div className="rp-bg-decoration rp-bg-decoration-3"></div>

      <div className="rp-wrapper">
        <div className="rp-card">
          {/* Icon */}
          <div className="rp-icon-wrapper">
            <div className="rp-icon">
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
          <div className="rp-header">
            <h1 className="rp-title">Set New Password</h1>
            {!missingParams && (
              <div className="rp-user-badge">
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
                <span>{usernameFromLink}</span>
              </div>
            )}
          </div>

          {missingParams ? (
            <div className="rp-error-state">
              <div className="rp-error-icon">
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  viewBox="0 0 24 24" 
                  fill="none" 
                  stroke="currentColor" 
                  strokeWidth="2"
                >
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="8" x2="12" y2="12"></line>
                  <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
              </div>
              <h3>Invalid Reset Link</h3>
              <p>The password reset link is invalid or has expired.</p>
              <Link to="/forgot-password" className="rp-back-link">
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
                Request New Reset Link
              </Link>
            </div>
          ) : (
            <>
              <form className="rp-form" onSubmit={onSubmit}>
                {/* New Password */}
                <div className="rp-input-group">
                  <label htmlFor="newPassword" className="rp-label">
                    New Password
                  </label>
                  <div className="rp-input-wrapper">
                    <span className="rp-input-icon">
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
                    </span>
                    <input
                      id="newPassword"
                      name="newPassword"
                      type={showPassword ? "text" : "password"}
                      className="rp-input"
                      placeholder="Enter new password"
                      value={form.newPassword}
                      onChange={onChange}
                      autoComplete="new-password"
                      disabled={submitting}
                    />
                    <button
                      type="button"
                      className="rp-toggle-password"
                      onClick={() => setShowPassword(!showPassword)}
                      tabIndex={-1}
                    >
                      {showPassword ? (
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                          <line x1="1" y1="1" x2="23" y2="23"></line>
                        </svg>
                      ) : (
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                          <circle cx="12" cy="12" r="3"></circle>
                        </svg>
                      )}
                    </button>
                  </div>
                  
                  {/* Password Strength Indicator */}
                  {form.newPassword && (
                    <div className="rp-strength">
                      <div className="rp-strength-bars">
                        {[1, 2, 3, 4].map((level) => (
                          <div
                            key={level}
                            className={`rp-strength-bar ${
                              level <= passwordStrength.level ? "active" : ""
                            }`}
                            style={{
                              backgroundColor:
                                level <= passwordStrength.level
                                  ? passwordStrength.color
                                  : "#e5e7eb",
                            }}
                          ></div>
                        ))}
                      </div>
                      <span
                        className="rp-strength-text"
                        style={{ color: passwordStrength.color }}
                      >
                        {passwordStrength.text}
                      </span>
                    </div>
                  )}
                </div>

                {/* Confirm Password */}
                <div className="rp-input-group">
                  <label htmlFor="confirm" className="rp-label">
                    Confirm New Password
                  </label>
                  <div className="rp-input-wrapper">
                    <span className="rp-input-icon">
                      <svg 
                        xmlns="http://www.w3.org/2000/svg" 
                        viewBox="0 0 24 24" 
                        fill="none" 
                        stroke="currentColor" 
                        strokeWidth="2"
                      >
                        <polyline points="20 6 9 17 4 12"></polyline>
                      </svg>
                    </span>
                    <input
                      id="confirm"
                      name="confirm"
                      type={showConfirm ? "text" : "password"}
                      className="rp-input"
                      placeholder="Confirm new password"
                      value={form.confirm}
                      onChange={onChange}
                      autoComplete="new-password"
                      disabled={submitting}
                    />
                    <button
                      type="button"
                      className="rp-toggle-password"
                      onClick={() => setShowConfirm(!showConfirm)}
                      tabIndex={-1}
                    >
                      {showConfirm ? (
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                          <line x1="1" y1="1" x2="23" y2="23"></line>
                        </svg>
                      ) : (
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                          <circle cx="12" cy="12" r="3"></circle>
                        </svg>
                      )}
                    </button>
                  </div>
                  {form.confirm && form.newPassword !== form.confirm && (
                    <p className="rp-input-error">Passwords do not match</p>
                  )}
                </div>

                {/* Requirements */}
                <div className="rp-requirements">
                  <p className="rp-requirements-title">Password must contain:</p>
                  <ul className="rp-requirements-list">
                    <li className={form.newPassword.length >= 8 ? "valid" : ""}>
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="20 6 9 17 4 12"></polyline>
                      </svg>
                      At least 8 characters
                    </li>
                    <li className={/[A-Z]/.test(form.newPassword) && /[a-z]/.test(form.newPassword) ? "valid" : ""}>
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="20 6 9 17 4 12"></polyline>
                      </svg>
                      Upper & lowercase letters
                    </li>
                    <li className={/\d/.test(form.newPassword) ? "valid" : ""}>
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="20 6 9 17 4 12"></polyline>
                      </svg>
                      At least one number
                    </li>
                    <li className={/[^A-Za-z0-9]/.test(form.newPassword) ? "valid" : ""}>
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="20 6 9 17 4 12"></polyline>
                      </svg>
                      At least one special character
                    </li>
                  </ul>
                </div>

                {/* Submit Button */}
                <button 
                  type="submit" 
                  className="rp-submit-btn" 
                  disabled={!canSubmit || submitting}
                >
                  {submitting ? (
                    <>
                      <span className="rp-spinner"></span>
                      Updating Password...
                    </>
                  ) : (
                    <>
                      <span>Update Password</span>
                      <svg 
                        xmlns="http://www.w3.org/2000/svg" 
                        viewBox="0 0 24 24" 
                        fill="none" 
                        stroke="currentColor" 
                        strokeWidth="2"
                      >
                        <polyline points="20 6 9 17 4 12"></polyline>
                      </svg>
                    </>
                  )}
                </button>
              </form>

              {/* Messages */}
              {msg && (
                <div className="rp-message rp-message-success">
                  <svg 
                    xmlns="http://www.w3.org/2000/svg" 
                    viewBox="0 0 24 24" 
                    fill="none" 
                    stroke="currentColor" 
                    strokeWidth="2"
                  >
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                  <span>{msg}</span>
                </div>
              )}
              
              {err && (
                <div className="rp-message rp-message-error">
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
              <div className="rp-footer">
                <Link to="/signin" className="rp-link">
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
            </>
          )}
        </div>
      </div>
    </div>
  );
}
