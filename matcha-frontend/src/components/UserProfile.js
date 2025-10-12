// src/pages/UserProfile.jsx
import React, { useEffect, useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../utils/api";
import "./user-profile.css";

const FALLBACK_AVATAR =
  "https://static-00.iconduck.com/assets.00/user-avatar-1024x1024-2xhpdo1n.png";

const API_BASE = "http://localhost:5000";

/**
 * Convert relative image paths to absolute URLs
 * Handles both /static/profiles/... and /profiles/... (for backward compatibility)
 */
function toAbsoluteUrl(url) {
  if (!url) return FALLBACK_AVATAR;
  if (/^https?:\/\//i.test(url)) return url;

  let cleanUrl = url.replace(/^\/+/, "");
  
  // If the URL doesn't start with 'static/' but starts with 'profiles/', add 'static/' prefix
  if (cleanUrl.startsWith("profiles/") && !cleanUrl.startsWith("static/")) {
    cleanUrl = `static/${cleanUrl}`;
  }
  
  return `${API_BASE}/${cleanUrl}`;
}

export default function UserProfile() {
  const { username: routeUsername } = useParams();
  const navigate = useNavigate();

  const [profile, setProfile] = useState(null); // full profile result
  const [avatar, setAvatar] = useState(FALLBACK_AVATAR);
  const [images, setImages] = useState([]);
  const [matched, setMatched] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState(null);
  const username = useMemo(() => routeUsername?.trim() || "", [routeUsername]);

  useEffect(() => {
    let mounted = true;

    async function load() {
      try {
        setErr(null);
        // 1) Viewing the profile logs the visit in your backend (you do this in get_profile)
        const res = await api.userProfile(username);
        const json = await res.json();
        if (!res.ok) throw new Error(json?.error || "Failed to load profile");
        const r = json.result || {};

        const picRes = await api.userProfilePic(username).catch(() => null);
        let picUrl = FALLBACK_AVATAR;
        if (picRes && picRes.ok) {
          const pj = await picRes.json().catch(() => ({}));
          if (pj?.result) {
            picUrl = toAbsoluteUrl(pj.result);
          }
        }
        const imgsRes = await api.userImages(username).catch(() => null);
        let gallery = [];
        if (imgsRes && imgsRes.ok) {
          const ij = await imgsRes.json().catch(() => ({}));
          if (Array.isArray(ij?.result)) {
            // Convert relative paths to absolute URLs
            gallery = ij.result.map(url => toAbsoluteUrl(url));
          }
        }
        const matchRes = await api.isMatched(username);
        const matchJson = await matchRes.json().catch(() => ({}));
        const isMatched = !!(matchRes.ok && matchJson?.result === true);

        if (mounted) {
          setProfile(r);
          setAvatar(picUrl);
          setImages(gallery);
          setMatched(isMatched);
        }
      } catch (e) {
        if (mounted) setErr(e.message || "Failed to load profile");
      }
    }

    if (username) load();
    return () => void (mounted = false);
  }, [username]);

  const onLikeToggle = async () => {
    if (!username) return;
    try {
      setBusy(true);
      const res = await api.likeDislike(username);
      const j = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(j?.error || "Failed to like/dislike");
      // Optionally refresh “matched” after like
      const mRes = await api.isMatched(username);
      const mJson = await mRes.json().catch(() => ({}));
      setMatched(!!(mRes.ok && mJson?.result === true));
    } catch (e) {
      alert(e.message || "Action failed");
    } finally {
      setBusy(false);
    }
  };

  const onBlock = async () => {
    if (!username) return;
    if (!window.confirm(`Block ${username}? They will no longer see you or interact.`)) return;
    try {
      setBusy(true);
      const res = await api.block(username);
      const j = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(j?.error || "Block failed");
      alert("User blocked.");
      navigate("/dashboard");
    } catch (e) {
      alert(e.message || "Block failed");
    } finally {
      setBusy(false);
    }
  };

  const onUnblock = async () => {
    if (!username) return;
    try {
      setBusy(true);
      const res = await api.unblock(username);
      const j = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(j?.error || "Unblock failed");
      alert("User unblocked.");
    } catch (e) {
      alert(e.message || "Unblock failed");
    } finally {
      setBusy(false);
    }
  };

  const onReport = async () => {
    if (!username) return;
    if (!window.confirm(`Report ${username} as fake?`)) return;
    try {
      setBusy(true);
      const res = await api.report(username);
      const j = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(j?.error || "Report failed");
      alert("User reported.");
    } catch (e) {
      alert(e.message || "Report failed");
    } finally {
      setBusy(false);
    }
  };

  if (!username) return <div className="user-wrap"><p>Missing username.</p></div>;
  if (err) return <div className="user-wrap"><p className="error">{err}</p></div>;
  if (!profile) return <div className="user-wrap"><div className="loading">Loading…</div></div>;

  const {
    first_name,
    last_name,
    username: uname,
    bio,
    gender,
    sexual_preferences,
    age,
    fame_rating,
    active,
    last_seen,
    location, // if your get_profile_data adds it
    tags,     // if your get_profile_data adds tags
  } = profile;

  const fullName = [first_name, last_name].filter(Boolean).join(" ") || uname || username;

  return (
    <div className="user-wrap">
      {/* Hero Header with Gradient */}
      <header className="user-header">
        <div className="header-gradient"></div>
        <div className="header-content">
          <div className="avatar-wrapper">
            <img className="user-avatar" src={avatar || FALLBACK_AVATAR} alt={fullName} />
            {active === true && <span className="online-badge">Online</span>}
          </div>
          <div className="user-info">
            <h1 className="user-name">{fullName}</h1>
            <div className="user-meta">
              {age && <span className="meta-item">🎂 {age} years old</span>}
              {gender && <span className="meta-item">👤 {gender}</span>}
              {location && <span className="meta-item">📍 {location}</span>}
            </div>
            <div className="fame-badge">
              <span className="fame-icon">⭐</span>
              <span className="fame-value">{Number(fame_rating || 0)}</span>
              <span className="fame-label">Fame Rating</span>
            </div>
          </div>
        </div>
      </header>

      <div className="user-content">
        {/* Info Card */}
        <div className="info-card">
          {sexual_preferences && (
            <div className="info-row">
              <span className="info-label">💕 Interested in</span>
              <span className="info-value">{sexual_preferences}</span>
            </div>
          )}
          {active === false && last_seen && (
            <div className="info-row">
              <span className="info-label">🕐 Last seen</span>
              <span className="info-value">{new Date(last_seen).toLocaleString()}</span>
            </div>
          )}
        </div>

        {/* Bio Section */}
        {bio && (
          <section className="user-section">
            <h3 className="section-title">About Me</h3>
            <p className="bio-text">{bio}</p>
          </section>
        )}

        {/* Interests Section */}
        {Array.isArray(tags) && tags.length > 0 && (
          <section className="user-section">
            <h3 className="section-title">Interests</h3>
            <div className="chip-row">
              {tags.map((t, i) => (
                <span className="interest-chip" key={`${t}-${i}`}>
                  {t}
                </span>
              ))}
            </div>
          </section>
        )}

        {/* Photos Gallery */}
        {images && images.length > 0 && (
          <section className="user-section">
            <h3 className="section-title">Photos ({images.length})</h3>
            <div className="photo-gallery">
              {images.map((src, i) => (
                <div key={i} className="gallery-item">
                  <img src={src} alt={`Photo ${i + 1}`} className="gallery-img" />
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Action Buttons */}
        <section className="user-actions">
          <button disabled={busy} className="action-btn primary" onClick={onLikeToggle}>
            <span className="btn-icon">{matched ? "💔" : "💖"}</span>
            {matched ? "Unlike" : "Like"}
          </button>

          {matched && (
            <button
              disabled={busy}
              className="action-btn success"
              onClick={() => navigate(`/messages?with=${encodeURIComponent(username)}`)}
            >
              <span className="btn-icon">💬</span>
              Send Message
            </button>
          )}

          <button disabled={busy} className="action-btn secondary" onClick={onUnblock}>
            <span className="btn-icon">🔓</span>
            Unblock
          </button>

          <button disabled={busy} className="action-btn warning" onClick={onBlock}>
            <span className="btn-icon">🚫</span>
            Block
          </button>

          <button disabled={busy} className="action-btn danger" onClick={onReport}>
            <span className="btn-icon">🚩</span>
            Report
          </button>
        </section>
      </div>
    </div>
  );
}
