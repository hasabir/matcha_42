// src/components/LandingPage.js
import React from "react";
import { useNavigate } from "react-router-dom";
import "./landingpage.css";

function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing-container">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-badge">
            <span className="hero-emoji">✨</span>
            <span>Welcome to Matcha</span>
          </div>
          <h1 className="hero-title">
            Find Your Perfect
            <span className="gradient-text"> Match</span>
          </h1>
          <p className="hero-subtitle">
            Connect with like-minded people, discover meaningful relationships,
            and start your journey to love today.
          </p>
          <div className="hero-buttons">
            <button className="btn-hero-primary" onClick={() => navigate("/register")}>
              Get Started Free
              <span className="btn-arrow">→</span>
            </button>
            <button className="btn-hero-secondary" onClick={() => navigate("/signin")}>
              Sign In
            </button>
          </div>
          <div className="hero-stats">
            <div className="stat-item">
              <span className="stat-number">10K+</span>
              <span className="stat-label">Active Users</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">5K+</span>
              <span className="stat-label">Matches Made</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">98%</span>
              <span className="stat-label">Success Rate</span>
            </div>
          </div>
        </div>
        <div className="hero-illustration">
          <div className="floating-card card-1">
            <div className="card-avatar">👨</div>
            <div className="card-info">
              <div className="card-name">Alex, 28</div>
              <div className="card-tags">🎨 Art • 🎵 Music</div>
            </div>
          </div>
          <div className="floating-card card-2">
            <div className="card-avatar">👩</div>
            <div className="card-info">
              <div className="card-name">Sara, 26</div>
              <div className="card-tags">📚 Books • ☕ Coffee</div>
            </div>
          </div>
          <div className="floating-card card-3">
            <div className="card-avatar">👨</div>
            <div className="card-info">
              <div className="card-name">Mike, 30</div>
              <div className="card-tags">🏃 Sports • 🎮 Gaming</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="section-header">
          <h2 className="section-title">Why Choose Matcha?</h2>
          <p className="section-subtitle">
            Everything you need to find your perfect match
          </p>
        </div>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <h3 className="feature-title">Smart Matching</h3>
            <p className="feature-desc">
              Our algorithm finds compatible matches based on interests, location, and preferences.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">💬</div>
            <h3 className="feature-title">Real-Time Chat</h3>
            <p className="feature-desc">
              Connect instantly with your matches through our fast, secure messaging system.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🔒</div>
            <h3 className="feature-title">Safe & Secure</h3>
            <p className="feature-desc">
              Your privacy matters. Block, report, and control who can see your profile.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📍</div>
            <h3 className="feature-title">Location-Based</h3>
            <p className="feature-desc">
              Find people nearby or explore matches in different cities.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⭐</div>
            <h3 className="feature-title">Fame Rating</h3>
            <p className="feature-desc">
              Build your reputation through genuine interactions and connections.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🔔</div>
            <h3 className="feature-title">Live Notifications</h3>
            <p className="feature-desc">
              Get instant alerts for likes, messages, and profile visits.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content">
          <h2 className="cta-title">Ready to Find Your Match?</h2>
          <p className="cta-subtitle">
            Join thousands of happy couples who found love on Matcha
          </p>
          <button className="cta-button" onClick={() => navigate("/register")}>
            Create Your Free Account
            <span className="cta-emoji">💕</span>
          </button>
        </div>
      </section>
    </div>
  );
}

export default LandingPage;
