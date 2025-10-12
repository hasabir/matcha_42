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
            <span className="hero-emoji">💕</span>
            <span>Join 10,000+ Happy Couples</span>
          </div>
          
          <h1 className="hero-title">
            Find Your <span className="gradient-text">Perfect Match</span>
          </h1>
          
          <p className="hero-subtitle">
            Connect with like-minded individuals and discover meaningful relationships.
            Join our community today and start your journey to love.
          </p>
          
          <div className="hero-buttons">
            <button 
              className="btn-hero-primary" 
              onClick={() => navigate("/register")}
            >
              Get Started Free
              <span className="btn-arrow">→</span>
            </button>
            <button 
              className="btn-hero-secondary" 
              onClick={() => navigate("/signin")}
            >
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
              <div className="card-tags">Music • Travel</div>
            </div>
          </div>
          
          <div className="floating-card card-2">
            <div className="card-avatar">👩</div>
            <div className="card-info">
              <div className="card-name">Sarah, 26</div>
              <div className="card-tags">Art • Coffee</div>
            </div>
          </div>
          
          <div className="floating-card card-3">
            <div className="card-avatar">🧑</div>
            <div className="card-info">
              <div className="card-name">Jordan, 30</div>
              <div className="card-tags">Sports • Food</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="section-header">
          <h2 className="section-title">Why Choose MatchUp?</h2>
          <p className="section-subtitle">
            Everything you need to find your perfect match
          </p>
        </div>
        
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <h3 className="feature-title">Smart Matching</h3>
            <p className="feature-desc">
              Our advanced algorithm finds compatible matches based on your interests,
              values, and preferences.
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">💬</div>
            <h3 className="feature-title">Real-Time Chat</h3>
            <p className="feature-desc">
              Connect instantly with your matches through our seamless messaging
              platform. Start conversations that matter.
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">🔒</div>
            <h3 className="feature-title">Safe & Secure</h3>
            <p className="feature-desc">
              Your privacy and security are our top priorities. All profiles are
              verified and your data is encrypted.
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3 className="feature-title">Instant Notifications</h3>
            <p className="feature-desc">
              Never miss a match! Get notified when someone likes your profile or
              sends you a message.
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">🌍</div>
            <h3 className="feature-title">Location-Based</h3>
            <p className="feature-desc">
              Find matches near you or expand your search radius to connect with
              people in different areas.
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">✨</div>
            <h3 className="feature-title">Profile Customization</h3>
            <p className="feature-desc">
              Express yourself with photos, interests, and a personalized bio that
              showcases your unique personality.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content">
          <h2 className="cta-title">Ready to Find Your Perfect Match?</h2>
          <p className="cta-subtitle">
            Join thousands of happy couples who found love on MatchUp.
            Your journey starts here!
          </p>
          <button 
            className="cta-button" 
            onClick={() => navigate("/register")}
          >
            <span className="cta-emoji">💕</span>
            Start Your Journey
          </button>
        </div>
      </section>
    </div>
  );
}

export default LandingPage;
