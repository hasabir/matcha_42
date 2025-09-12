// src/components/LandingPage.js
import React from "react";
import { useNavigate } from "react-router-dom";
import "./landingpage.css";
import homeImage from "./images/home_image.jpg";  // <-- import here

function LandingPage() {
  const navigate = useNavigate();

  return (
    <div
      className="landing-container"
      style={{
        background: `url(${homeImage}) no-repeat center center/cover`
      }}
    >
      <div className="landing-overlay">
        <h1 className="landing-title">Find Your Perfect Match</h1>
        <p className="landing-subtitle">
          Connect with like-minded individuals and discover meaningful relationships.
          Join our community today and start your journey to love.
        </p>
        <div className="landing-buttons">
          <button className="join-btn" onClick={() => navigate("/register")}>
            Join Now
          </button>
          <button className="login-btn" onClick={() => navigate("/signin")}>
            Log In
          </button>
        </div>
      </div>
    </div>
  );
}

export default LandingPage;
