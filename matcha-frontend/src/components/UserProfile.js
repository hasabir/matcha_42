// src/pages/UserProfile.jsx
import React, { useEffect, useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../utils/api";
import "./user-profile.css";

const FALLBACK_AVATAR =
  "https://static-00.iconduck.com/assets.00/user-avatar-1024x1024-2xhpdo1n.png";

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
          if (pj?.result) picUrl = pj.result;
        }
        const imgsRes = await api.userImages(username).catch(() => null);
        let gallery = [];
        if (imgsRes && imgsRes.ok) {
          const ij = await imgsRes.json().catch(() => ({}));
          if (Array.isArray(ij?.result)) gallery = ij.result;
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
      <header className="user-header">
        <img className="user-avatar" src={avatar || FALLBACK_AVATAR} alt={fullName} />
        <div className="user-title">
          <h1>{fullName}</h1>
          <p className="dim">
            Fame rating: <strong>{Number(fame_rating || 0)}</strong>
            {active === true && <span className="online-dot" title="Online" />}
            {active === false && last_seen && (
              <span className="last-seen"> — last seen {new Date(last_seen).toLocaleString()}</span>
            )}
          </p>
          {age && <p className="dim">Age: {age}</p>}
          {gender && <p className="dim">Gender: {gender}</p>}
          {sexual_preferences && <p className="dim">Interested in: {sexual_preferences}</p>}
          {location && <p className="dim">Location: {location}</p>}
        </div>
      </header>

      {bio && (
        <section className="user-section">
          <h3>About</h3>
          <p>{bio}</p>
        </section>
      )}

      {Array.isArray(tags) && tags.length > 0 && (
        <section className="user-section">
          <h3>Interests</h3>
          <div className="chip-row">
            {tags.map((t, i) => (
              <span className="chip" key={`${t}-${i}`}>#{t}</span>
            ))}
          </div>
        </section>
      )}

      {images && images.length > 0 && (
        <section className="user-section">
          <h3>Photos</h3>
          <div className="gallery">
            {images.map((src, i) => (
              <img key={i} src={src} alt={`img-${i}`} className="gallery-img" />
            ))}
          </div>
        </section>
      )}

      {/* Actions */}
      <section className="user-actions">
        <button disabled={busy} className="pill-btn primary" onClick={onLikeToggle}>
          {matched ? "Unlike" : "Like"}
        </button>

        <button disabled={busy} className="pill-btn" onClick={() => navigate(`/messages?with=${encodeURIComponent(username)}`)} hidden={!matched}>
          Chat
        </button>

        <button disabled={busy} className="pill-btn warn" onClick={onBlock}>
          Block
        </button>

        <button disabled={busy} className="pill-btn" onClick={onUnblock}>
          Unblock
        </button>

        <button disabled={busy} className="pill-btn danger" onClick={onReport}>
          Report
        </button>
      </section>
    </div>
  );
}
