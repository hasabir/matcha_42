// src/pages/Dashboard.jsx
import React, { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { api, BASE } from "../utils/api";
import "./dashboard.css";

const FALLBACK_AVATAR =
  "https://cdn-icons-png.flaticon.com/512/149/149071.png";

const API_BASE = process.env.REACT_APP_API_BASE || BASE;

/**
 * Ensure we use an absolute URL for images no matter what backend returns.
 * If API already sends absolute URLs (recommended), this is a no-op.
 * Handles both /static/profiles/... and /profiles/... (for backward compatibility)
 */
function toAbsoluteUrl(url) {
  if (!url) return FALLBACK_AVATAR;
  if (/^https?:\/\//i.test(url)) return url;

  // Construct absolute URL from relative path
  try {
    let cleanUrl = url.replace(/^\/+/, ""); // Remove leading slashes
    
    // If the URL doesn't start with 'static/' but starts with 'profiles/', add 'static/' prefix
    if (cleanUrl.startsWith("profiles/") && !cleanUrl.startsWith("static/")) {
      cleanUrl = `static/${cleanUrl}`;
    }
    
    return `${API_BASE.replace(/\/+$/, "")}/${cleanUrl}`;
  } catch {
    return url.startsWith("/") ? `${API_BASE}${url}` : `${API_BASE}/${url}`;
  }
}

export default function Dashboard() {
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [profilePic, setProfilePic] = useState(FALLBACK_AVATAR);
  const [stats, setStats] = useState({ likes: 0, messages: 0, views: 0 });
  const [viewers, setViewers] = useState([]);
  const [likedUsers, setLikedUsers] = useState([]);
  const [likers, setLikers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Stable onError handler that won’t loop forever
  const onImgError = useMemo(
    () => (e) => {
      if (e?.target?.src !== FALLBACK_AVATAR) {
        e.target.src = FALLBACK_AVATAR;
      }
    },
    []
  );

  useEffect(() => {
    let mounted = true;
    const ctrl = new AbortController();

    async function loadDashboard() {
      try {
        setLoading(true);
        setError(null);

        // 1) Load current user profile
        const meRes = await api.meProfile({ signal: ctrl.signal });
        const meData = await meRes.json();

        if (!meRes.ok) {
          throw new Error(meData?.error || "Failed to load profile");
        }

        const userData = meData.result || {};
        if (!mounted) return;
        setUser(userData);

        // 2) Load profile picture (always absolute from backend; helper still guards)
        try {
          const picRes = await api.myProfilePic({ signal: ctrl.signal });
          const picData = await picRes.json();

          if (!mounted) return;
          if (picRes.ok) {
            const url = toAbsoluteUrl(picData?.result);
            setProfilePic(url || FALLBACK_AVATAR);
          }
        } catch (err) {
          console.error("Failed to load profile picture:", err);
        }

        // 3) Load visitors
        try {
          const visRes = await api.myVisitors({ signal: ctrl.signal });
          const visData = await visRes.json();

          if (visRes.ok && Array.isArray(visData.result)) {
            const viewersWithPics = await Promise.all(
              visData.result.map(async (visitor) => {
                try {
                  const picRes = await api.userProfilePic(visitor.username, {
                    signal: ctrl.signal,
                  });
                  const picData = await picRes.json();
                  const picUrl = picRes.ok ? toAbsoluteUrl(picData?.result) : FALLBACK_AVATAR;
                  return {
                    ...visitor,
                    avatar: picUrl || FALLBACK_AVATAR,
                  };
                } catch {
                  return { ...visitor, avatar: FALLBACK_AVATAR };
                }
              })
            );
            if (!mounted) return;
            setViewers(viewersWithPics);
            setStats((prev) => ({ ...prev, views: viewersWithPics.length }));
          }
        } catch (err) {
          console.error("Failed to load visitors:", err);
        }

        // 4) Load liked users
        try {
          const likedRes = await api.getUsers("liked", { signal: ctrl.signal });
          const likedData = await likedRes.json();

          if (likedRes.ok && Array.isArray(likedData.result)) {
            const likedWithDetails = await Promise.all(
              likedData.result.map(async (username) => {
                try {
                  const [matchRes, picRes] = await Promise.all([
                    api.isMatched(username, { signal: ctrl.signal }),
                    api.userProfilePic(username, { signal: ctrl.signal }),
                  ]);
                  const matchData = await matchRes.json();
                  const picData = await picRes.json();
                  const picUrl = picRes.ok ? toAbsoluteUrl(picData?.result) : FALLBACK_AVATAR;

                  return {
                    username,
                    matched: matchRes.ok && matchData?.result === true,
                    avatar: picUrl || FALLBACK_AVATAR,
                  };
                } catch {
                  return { username, matched: false, avatar: FALLBACK_AVATAR };
                }
              })
            );
            if (!mounted) return;
            setLikedUsers(likedWithDetails);
          }
        } catch (err) {
          console.error("Failed to load liked users:", err);
        }

        // 5) Load likers
        try {
          const likersRes = await api.getUsers("likers", { signal: ctrl.signal });
          const likersData = await likersRes.json();

          if (likersRes.ok && Array.isArray(likersData.result)) {
            const likersWithDetails = await Promise.all(
              likersData.result.map(async (username) => {
                try {
                  const [matchRes, picRes] = await Promise.all([
                    api.isMatched(username, { signal: ctrl.signal }),
                    api.userProfilePic(username, { signal: ctrl.signal }),
                  ]);
                  const matchData = await matchRes.json();
                  const picData = await picRes.json();
                  const picUrl = picRes.ok ? toAbsoluteUrl(picData?.result) : FALLBACK_AVATAR;

                  return {
                    username,
                    matched: matchRes.ok && matchData?.result === true,
                    avatar: picUrl || FALLBACK_AVATAR,
                  };
                } catch {
                  return { username, matched: false, avatar: FALLBACK_AVATAR };
                }
              })
            );
            if (!mounted) return;
            setLikers(likersWithDetails);
            setStats((prev) => ({ ...prev, likes: likersWithDetails.length }));
          }
        } catch (err) {
          console.error("Failed to load likers:", err);
        }
      } catch (err) {
        if (mounted) {
          setError(err?.message || "Failed to load dashboard");
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }

    loadDashboard();
    return () => {
      mounted = false;
      ctrl.abort();
    };
  }, []);

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-state">Loading your dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="error-state">
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="dashboard-container">
        <div className="error-state">No user data available</div>
      </div>
    );
  }

  const displayName =
    user.first_name && user.last_name
      ? `${user.first_name} ${user.last_name}`
      : user.username;

  return (
    <div className="dashboard-container">
      {/* Profile Header */}
      <div className="profile-header">
        <div
          className="profile-pic"
          onClick={() => navigate("/settings")}
          style={{ cursor: "pointer" }}
        >
          <img src={profilePic} alt="Profile" onError={onImgError} />
          <span className="profile-label">Profile</span>
        </div>
        <h1 className="welcome-text">Welcome back, {displayName}!</h1>
        <p className="fame-rating">Fame rating: {user.fame_rating || 5}</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-container">
        <div className="stat-card">
          <h3>New Likes</h3>
          <p className="stat-number">{stats.likes}</p>
        </div>
        <div className="stat-card">
          <h3>New Messages</h3>
          <p className="stat-number">{stats.messages}</p>
        </div>
        <div className="stat-card">
          <h3>Profile Views</h3>
          <p className="stat-number">{stats.views}</p>
        </div>
      </div>

      {/* Recent Viewers */}
      <div className="dashboard-section">
        <div className="section-header">
          <h2>Recent Viewers</h2>
          <button className="view-all-btn" onClick={() => navigate("/discover")}>
            View All
          </button>
        </div>
        <div className="users-grid">
          {viewers.length > 0 ? (
            viewers.slice(0, 12).map((viewer, index) => (
              <div
                key={`${viewer.username}-${index}`}
                className="user-card"
                onClick={() => navigate(`/u/${viewer.username}`)}
              >
                <img src={viewer.avatar} alt={viewer.username} onError={onImgError} />
                <p className="username">{viewer.username}</p>
              </div>
            ))
          ) : (
            <p className="no-data">No recent viewers</p>
          )}
        </div>
      </div>

      {/* Profiles You Liked */}
      <div className="dashboard-section">
        <div className="section-header">
          <h2>Profiles You Liked</h2>
          <button className="view-all-btn" onClick={() => navigate("/discover")}>
            Discover more
          </button>
        </div>
        <div className="users-grid">
          {likedUsers.length > 0 ? (
            likedUsers.slice(0, 16).map((u, index) => (
              <div
                key={`${u.username}-${index}`}
                className="user-card"
                onClick={() => navigate(`/u/${u.username}`)}
              >
                <img src={u.avatar} alt={u.username} onError={onImgError} />
                <p className="username">{u.username}</p>
                {u.matched && <span className="match-badge">Matched</span>}
              </div>
            ))
          ) : (
            <p className="no-data">You haven't liked anyone yet</p>
          )}
        </div>
      </div>

      {/* They Liked You */}
      <div className="dashboard-section">
        <div className="section-header">
          <h2>They Liked You</h2>
        </div>
        <div className="users-grid">
          {likers.length > 0 ? (
            likers.slice(0, 16).map((u, index) => (
              <div
                key={`${u.username}-${index}`}
                className="user-card"
                onClick={() => navigate(`/u/${u.username}`)}
              >
                <img src={u.avatar} alt={u.username} onError={onImgError} />
                <p className="username">{u.username}</p>
                {u.matched && <span className="match-badge">Matched</span>}
              </div>
            ))
          ) : (
            <p className="no-data">No one has liked you yet</p>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2>Quick Actions</h2>
        <button className="action-btn" onClick={() => navigate("/settings")}>
          Edit Profile
        </button>
        <button className="action-btn" onClick={() => navigate("/messages")}>
          Check My Messages
        </button>
      </div>
    </div>
  );
}
