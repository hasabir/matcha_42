import React from "react";
import { Link, useNavigate } from "react-router-dom";
import "./dashboard.css";

const Dashboard = () => {
  const navigate = useNavigate();

  // (Stub data — replace with API later)
  const stats = {
    likes: 3,
    messages: 5,
    views: 12,
    name: "Amelia",
    avatar:
      "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=256&h=256&fit=crop&auto=format"
  };

  const recentViewers = [
    "https://i.pravatar.cc/48?img=11",
    "https://i.pravatar.cc/48?img=12",
    "https://i.pravatar.cc/48?img=13",
    "https://i.pravatar.cc/48?img=14",
  ];

  const recentLikes = [
    "https://i.pravatar.cc/48?img=21",
    "https://i.pravatar.cc/48?img=22",
    "https://i.pravatar.cc/48?img=23",
  ];

  return (
    <div className="dash-wrap">
      {/* Header */}
      <header className="dash-header">
        <img className="dash-avatar" src={stats.avatar} alt="Profile" />
        <div className="dash-hello">
          <h1>Welcome back, {stats.name}!</h1>
          <p>Ready to find your perfect match?</p>
        </div>
      </header>

      {/* Stats */}
      <section className="dash-cards">
        <article className="dash-card">
          <span className="dash-card-label">New Likes</span>
          <span className="dash-card-value">{stats.likes}</span>
        </article>

        <article className="dash-card">
          <span className="dash-card-label">New Messages</span>
          <span className="dash-card-value">{stats.messages}</span>
        </article>

        <article className="dash-card">
          <span className="dash-card-label">Profile Views</span>
          <span className="dash-card-value">{stats.views}</span>
        </article>
      </section>

      {/* Recent Viewers */}
      <section className="dash-block">
        <div className="dash-block-head">
          <h3>Recent Viewers</h3>
          <Link to="/discover" className="dash-muted-link">View All</Link>
        </div>
        <div className="avatar-row">
          {recentViewers.map((src, i) => (
            <img key={i} src={src} className="mini-avatar" alt="viewer" />
          ))}
        </div>
      </section>

      {/* Recent Likes */}
      <section className="dash-block">
        <div className="dash-block-head">
          <h3>Recent Likes</h3>
          <Link to="/discover" className="dash-muted-link">View All</Link>
        </div>
        <div className="avatar-row">
          {recentLikes.map((src, i) => (
            <img key={i} src={src} className="mini-avatar" alt="like" />
          ))}
        </div>
      </section>

      {/* Quick actions (wide pills) */}
      <section className="dash-quick">
        <h2>Quick Actions</h2>
        <button
          className="pill-btn"
          onClick={() => navigate("/settings")}
        >
          Edit Profile
        </button>
        <button
          className="pill-btn"
          onClick={() => navigate("/messages")}
        >
          Check My Messages
        </button>
      </section>
    </div>
  );
};

export default Dashboard;
