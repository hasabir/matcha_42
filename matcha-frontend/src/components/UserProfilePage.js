import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "./UserProfilePage.css";

const UserProfilePage = () => {
  const { username } = useParams();
  const navigate = useNavigate();
  
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [liked, setLiked] = useState(false);
  const [isMatch, setIsMatch] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [showReportModal, setShowReportModal] = useState(false);

  // Helper function to get image URL from either string or object format
  const getImageUrl = (img) => {
    if (!img) return null;
    return typeof img === 'string' ? img : img.image_url;
  };

  useEffect(() => {
    fetchProfile();
  }, [username]);

  const fetchProfile = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(`http://localhost:5000/api/profile/get_profile/${username}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch profile");
      }

      const data = await response.json();
      setProfile(data);
      
      // Check if already liked
      checkIfLiked();
      
      // Check if it's a match
      checkIfMatch();
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const checkIfLiked = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(`http://localhost:5000/api/interactions/my_likes`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        const hasLiked = data.some(user => user.username === username);
        setLiked(hasLiked);
      }
    } catch (err) {
      console.error("Error checking like status:", err);
    }
  };

  const checkIfMatch = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(`http://localhost:5000/api/interactions/my_connections`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        const matched = data.some(user => user.username === username);
        setIsMatch(matched);
      }
    } catch (err) {
      console.error("Error checking match status:", err);
    }
  };

  const handleLike = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const endpoint = liked 
        ? `http://localhost:5000/api/interactions/unlike/${profile.username}`
        : `http://localhost:5000/api/interactions/like/${profile.username}`;
      
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setLiked(!liked);
        const data = await response.json();
        
        // Check if it's a new match
        if (data.matched) {
          setIsMatch(true);
          alert("🎉 It's a Match! You can now chat with each other.");
        }
      }
    } catch (err) {
      console.error("Error liking profile:", err);
    }
  };

  const handleBlock = async () => {
    if (!window.confirm(`Are you sure you want to block ${profile.username}?`)) {
      return;
    }

    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(`http://localhost:5000/api/interactions/block/${profile.username}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        alert(`You have blocked ${profile.username}`);
        navigate("/discover");
      }
    } catch (err) {
      console.error("Error blocking user:", err);
    }
  };

  const handleReport = async (reason) => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(`http://localhost:5000/api/interactions/report`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          reported_username: profile.username,
          reason: reason,
        }),
      });

      if (response.ok) {
        alert("Report submitted successfully");
        setShowReportModal(false);
      }
    } catch (err) {
      console.error("Error reporting user:", err);
    }
  };

  const handleChat = () => {
    navigate(`/chat/${profile.username}`);
  };

  const nextImage = () => {
    if (profile.images && profile.images.length > 0) {
      setCurrentImageIndex((prev) => (prev + 1) % profile.images.length);
    }
  };

  const prevImage = () => {
    if (profile.images && profile.images.length > 0) {
      setCurrentImageIndex((prev) => (prev - 1 + profile.images.length) % profile.images.length);
    }
  };

  const calculateAge = (birthdate) => {
    if (!birthdate) return profile.age || "N/A";
    const today = new Date();
    const birth = new Date(birthdate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  };

  if (loading) {
    return (
      <div className="profile-loading">
        <div className="spinner"></div>
        <p>Loading profile...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="profile-error">
        <h2>Oops!</h2>
        <p>{error}</p>
        <button onClick={() => navigate("/discover")}>Back to Discover</button>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="profile-error">
        <h2>Profile not found</h2>
        <button onClick={() => navigate("/discover")}>Back to Discover</button>
      </div>
    );
  }

  const allImages = [
    profile.profile_picture,
    ...(profile.images || []).map(img => getImageUrl(img))
  ].filter(Boolean);

  return (
    <div className="user-profile-page">
      <div className="profile-container">
        {/* Back Button */}
        <button className="back-button" onClick={() => navigate(-1)}>
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          Back
        </button>

        <div className="profile-content">
          {/* Image Gallery */}
          <div className="profile-gallery">
            {allImages.length > 0 ? (
              <div className="gallery-main">
                <img 
                  src={`http://localhost:5000${allImages[currentImageIndex]}`} 
                  alt={`${profile.username}'s photo`}
                  onError={(e) => {
                    e.target.src = "/default-avatar.png";
                  }}
                />
                
                {allImages.length > 1 && (
                  <>
                    <button className="gallery-nav prev" onClick={prevImage}>
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="15 18 9 12 15 6"></polyline>
                      </svg>
                    </button>
                    <button className="gallery-nav next" onClick={nextImage}>
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="9 18 15 12 9 6"></polyline>
                      </svg>
                    </button>
                    
                    <div className="gallery-indicators">
                      {allImages.map((_, index) => (
                        <span
                          key={index}
                          className={`indicator ${index === currentImageIndex ? "active" : ""}`}
                          onClick={() => setCurrentImageIndex(index)}
                        ></span>
                      ))}
                    </div>
                  </>
                )}
                
                {isMatch && (
                  <div className="match-badge">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                    </svg>
                    It's a Match!
                  </div>
                )}
              </div>
            ) : (
              <div className="no-image">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
              </div>
            )}
          </div>

          {/* Profile Info */}
          <div className="profile-info">
            <div className="profile-header">
              <h1>
                {profile.first_name} {profile.last_name}
                <span className="username">@{profile.username}</span>
              </h1>
              <div className="profile-meta">
                <span className="age">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                    <line x1="16" y1="2" x2="16" y2="6"></line>
                    <line x1="8" y1="2" x2="8" y2="6"></line>
                    <line x1="3" y1="10" x2="21" y2="10"></line>
                  </svg>
                  {calculateAge(profile.birthdate)} years old
                </span>
                {profile.location && (
                  <span className="location">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                      <circle cx="12" cy="10" r="3"></circle>
                    </svg>
                    {profile.city}, {profile.country}
                    {profile.distance && ` • ${Math.round(profile.distance)} km away`}
                  </span>
                )}
                {profile.fame_rating !== undefined && (
                  <span className="fame-rating">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                    </svg>
                    {profile.fame_rating}/10
                  </span>
                )}
              </div>
            </div>

            {/* Bio */}
            {profile.bio && (
              <div className="profile-section">
                <h3>About</h3>
                <p className="bio">{profile.bio}</p>
              </div>
            )}

            {/* Details */}
            <div className="profile-section">
              <h3>Details</h3>
              <div className="details-grid">
                {profile.gender && (
                  <div className="detail-item">
                    <span className="detail-label">Gender</span>
                    <span className="detail-value">{profile.gender}</span>
                  </div>
                )}
                {profile.sexual_preferences && (
                  <div className="detail-item">
                    <span className="detail-label">Interested in</span>
                    <span className="detail-value">{profile.sexual_preferences}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Interests */}
            {profile.tags && profile.tags.length > 0 && (
              <div className="profile-section">
                <h3>Interests</h3>
                <div className="interests-list">
                  {profile.tags.map((tag, index) => (
                    <span key={index} className="interest-tag">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="profile-actions">
              {isMatch ? (
                <button className="action-btn primary chat" onClick={handleChat}>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                  </svg>
                  Send Message
                </button>
              ) : (
                <button 
                  className={`action-btn primary ${liked ? "liked" : ""}`} 
                  onClick={handleLike}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill={liked ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2">
                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                  </svg>
                  {liked ? "Unlike" : "Like"}
                </button>
              )}
              
              <button className="action-btn secondary" onClick={() => setShowReportModal(true)}>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                  <line x1="12" y1="9" x2="12" y2="13"></line>
                  <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
                Report
              </button>
              
              <button className="action-btn secondary danger" onClick={handleBlock}>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="4.93" y1="4.93" x2="19.07" y2="19.07"></line>
                </svg>
                Block
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Report Modal */}
      {showReportModal && (
        <div className="modal-overlay" onClick={() => setShowReportModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Report User</h2>
            <p>Why are you reporting {profile.username}?</p>
            <div className="report-reasons">
              <button onClick={() => handleReport("Fake profile")}>Fake profile</button>
              <button onClick={() => handleReport("Inappropriate content")}>Inappropriate content</button>
              <button onClick={() => handleReport("Harassment")}>Harassment</button>
              <button onClick={() => handleReport("Spam")}>Spam</button>
              <button onClick={() => handleReport("Other")}>Other</button>
            </div>
            <button className="cancel-btn" onClick={() => setShowReportModal(false)}>
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserProfilePage;
