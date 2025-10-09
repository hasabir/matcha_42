// src/pages/Dashboard.jsx
import React, { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, chatApi } from "../utils/api";
import "./dashboard.css";

const FALLBACK_AVATAR =
  "https://static-00.iconduck.com/assets.00/user-avatar-1024x1024-2xhpdo1n.png";

export default function Dashboard() {
  const navigate = useNavigate();

  const [me, setMe] = useState({
    username: "",
    first_name: "",
    last_name: "",
    fame_rating: 0,
    profile_picture: null,
    online: null,
    last_seen: null,
  });
  const [stats, setStats] = useState({ likes: 0, messages: 0, views: 0 });
  const [viewers, setViewers] = useState([]);         // [{ username, avatar }]
  const [likedUsers, setLikedUsers] = useState([]);   // [{ username, matched, avatar }]
  const [likers, setLikers] = useState([]);           // [{ username, matched, avatar }]
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);

  const displayName = useMemo(() => {
    const firstName = me.first_name?.trim();
    const lastName = me.last_name?.trim();
    
    if (firstName || lastName) {
      return `${firstName || ""} ${lastName || ""}`.trim();
    }
    return me.username?.trim() || "there";
  }, [me]);

  useEffect(() => {
    let mounted = true;

    async function load() {
      try {
        setLoading(true);
        setErr(null);

        // 1) Me
        const meRes = await api.meProfile();
        const meJson = await meRes.json();
        if (!meRes.ok) throw new Error(meJson?.error || "Failed to load profile");
        
        const r = meJson.result || {};
        const hydrated = {
          username: r.username || "",
          first_name: r.first_name || "",
          last_name: r.last_name || "",
          fame_rating: Number(r.fame_rating || 0),
          profile_picture: r.profile_picture || null,
          online: typeof r.active === "boolean" ? r.active : null,
          last_seen: r.last_seen || null,
        };

        if (!hydrated.profile_picture) {
          try {
            const picRes = await api.myProfilePic();
            const picJson = await picRes.json();
            if (picRes.ok && picJson?.result) hydrated.profile_picture = picJson.result;
          } catch {}
        }

        // Get unread message count
        let unreadCount = 0;
        try {
          const unreadRes = await chatApi.getUnreadCount();
          const unreadJson = await unreadRes.json();
          if (unreadRes.ok && unreadJson?.unread_count !== undefined) {
            unreadCount = unreadJson.unread_count;
          }
        } catch {
          // Ignore errors for unread count
        }

        // 2) Visitors
        const visRes = await api.myVisitors();
        const visJson = await visRes.json();
        if (!visRes.ok) throw new Error(visJson?.error || "Failed to load visitors");
        const rawVisitors = Array.isArray(visJson.result) ? visJson.result : [];
        const viewersResolved = await Promise.all(
          rawVisitors.map(async (row) => {
            const username = row?.username;
            if (!username) return { username: "", avatar: FALLBACK_AVATAR };
            try {
              const p = await api.userProfilePic(username);
              const j = await p.json();
              return { username, avatar: p.ok && j?.result ? j.result : FALLBACK_AVATAR };
            } catch {
              return { username, avatar: FALLBACK_AVATAR };
            }
          })
        );

        // 3) Liked / Likers + match flags + avatars
        const [likedRes, likersRes] = await Promise.all([api.getUsers("liked"), api.getUsers("likers")]);
        const likedJson = await likedRes.json();
        const likersJson = await likersRes.json();

        if (!likedRes.ok) throw new Error(likedJson?.error || "Failed to load liked");
        if (!likersRes.ok) throw new Error(likersJson?.error || "Failed to load likers");

        const likedList = Array.isArray(likedJson.result) ? likedJson.result : [];
        const likersList = Array.isArray(likersJson.result) ? likersJson.result : [];

        const decorate = async (username) => {
          try {
            const [mRes, picRes] = await Promise.all([api.isMatched(username), api.userProfilePic(username)]);
            const mJson = await mRes.json().catch(() => ({}));
            const pJson = await picRes.json().catch(() => ({}));
            const matched = !!(mRes.ok && mJson?.result === true);
            const avatar = picRes.ok && pJson?.result ? pJson.result : FALLBACK_AVATAR;
            return { username, matched, avatar };
          } catch {
            return { username, matched: false, avatar: FALLBACK_AVATAR };
          }
        };

        const [likedDecor, likersDecor] = await Promise.all([
          Promise.all(likedList.map(decorate)),
          Promise.all(likersList.map(decorate)),
        ]);

        if (mounted) {
          setMe(hydrated);
          setViewers(viewersResolved);
          setLikedUsers(likedDecor);
          setLikers(likersDecor);
          setStats({ 
            views: rawVisitors.length, 
            likes: likersDecor.length,
            messages: unreadCount
          });
        }
      } catch (e) {
        if (mounted) setErr(e.message || "Failed to load dashboard");
      } finally {
        if (mounted) setLoading(false);
      }
    }

    load();
    return () => void (mounted = false);
  }, []);

  if (loading) {
    return <div className="dash-wrap"><div className="dash-skeleton">Loading…</div></div>;
  }
  if (err) {
    return (
      <div className="dash-wrap">
        <div className="dash-error">
          <p>{err}</p>
          <button className="pill-btn" onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="dash-wrap">
      {/* Header */}
      <header className="dash-header">
        <img className="dash-avatar" src={me.profile_picture || FALLBACK_AVATAR} alt="Profile" />
        <div className="dash-hello">
          <h1>Welcome back, {displayName}!</h1>
          <p>
            Fame rating: <strong>{me.fame_rating}</strong>
            {me.online === true && <span className="online-dot" title="Online" />}
            {me.online === false && me.last_seen && (
              <span className="last-seen"> — last seen {new Date(me.last_seen).toLocaleString()}</span>
            )}
          </p>
        </div>
      </header>

      {/* Stats */}
      <section className="dash-cards">
        <article className="dash-card"><span className="dash-card-label">New Likes</span><span className="dash-card-value">{stats.likes}</span></article>
        <article className="dash-card"><span className="dash-card-label">New Messages</span><span className="dash-card-value">{stats.messages}</span></article>
        <article className="dash-card"><span className="dash-card-label">Profile Views</span><span className="dash-card-value">{stats.views}</span></article>
      </section>

      {/* Recent Viewers */}
      <section className="dash-block">
        <div className="dash-block-head">
          <h3>Recent Viewers</h3>
          <Link to="/discover" className="dash-muted-link">View All</Link>
        </div>
        <div className="avatar-row">
          {viewers.slice(0, 12).map((v, i) => (
            <button
              key={`${v.username}-${i}`}
              className="mini-avatar-btn"
              onClick={() => v.username && navigate(`/u/${encodeURIComponent(v.username)}`)}
              title={v.username}
            >
              <img src={v.avatar || FALLBACK_AVATAR} className="mini-avatar" alt={v.username || "viewer"} />
            </button>
          ))}
        </div>
      </section>

      {/* I liked */}
      <section className="dash-block">
        <div className="dash-block-head">
          <h3>Profiles You Liked</h3>
          <Link to="/discover" className="dash-muted-link">Discover more</Link>
        </div>
        <div className="avatar-row">
          {likedUsers.slice(0, 16).map((u) => (
            <button
              key={`liked-${u.username}`}
              className="mini-avatar-btn"
              onClick={() => navigate(`/u/${encodeURIComponent(u.username)}`)}
              title={u.username}
            >
              <img src={u.avatar} className="mini-avatar" alt={u.username} />
              {u.matched && <span className="badge">Matched</span>}
            </button>
          ))}
        </div>
      </section>

      {/* They liked me */}
      <section className="dash-block">
        <div className="dash-block-head">
          <h3>They Liked You</h3>
        </div>
        <div className="avatar-row">
          {likers.slice(0, 16).map((u) => (
            <button
              key={`liker-${u.username}`}
              className="mini-avatar-btn"
              onClick={() => navigate(`/u/${encodeURIComponent(u.username)}`)}
              title={u.username}
            >
              <img src={u.avatar} className="mini-avatar" alt={u.username} />
              {u.matched && <span className="badge">Matched</span>}
            </button>
          ))}
        </div>
      </section>

      {/* Quick actions */}
      <section className="dash-quick">
        <h2>Quick Actions</h2>
        <button className="pill-btn" onClick={() => navigate("/settings")}>Edit Profile</button>
        <button className="pill-btn" onClick={() => navigate("/messages")}>Check My Messages</button>
      </section>
    </div>
  );
}
