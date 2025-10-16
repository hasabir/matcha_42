import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchWithAuth } from '../utils/api';
import './UserProfileView.css';

const UserProfileView = () => {
  const { username } = useParams();
  const navigate = useNavigate();
  
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [liking, setLiking] = useState(false);
  const [passing, setPassing] = useState(false);
  const [actionResult, setActionResult] = useState(null);

  useEffect(() => {
    fetchUserProfile();
  }, [username]);

  const fetchUserProfile = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetchWithAuth(`http://localhost:5000/api/profile/get_profile/${username}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('User not found');
        } else if (response.status === 403) {
          throw new Error('You are blocked by this user');
        }
        throw new Error('Failed to load profile');
      }
      
      const data = await response.json();
      setProfile(data.result || data);
    } catch (err) {
      console.error('Error fetching user profile:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const calculateAge = (birthdate) => {
    if (!birthdate) return profile?.age || 'N/A';
    const today = new Date();
    const birth = new Date(birthdate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  };

  const handleLike = async () => {
    setLiking(true);
    setActionResult(null);
    
    try {
      const response = await fetchWithAuth(`http://localhost:5000/api/interactions/like/${username}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.match) {
          setActionResult({
            type: 'match',
            message: `🎉 It's a match! You can now chat with ${profile.first_name}!`
          });
        } else {
          setActionResult({
            type: 'like',
            message: `💖 You liked ${profile.first_name}. They'll be notified!`
          });
        }
        
        // Auto-redirect after 3 seconds
        setTimeout(() => {
          navigate('/discover');
        }, 3000);
      } else {
        throw new Error('Failed to send like');
      }
    } catch (err) {
      console.error('Error liking user:', err);
      setActionResult({
        type: 'error',
        message: '❌ Failed to send like. Please try again.'
      });
    } finally {
      setLiking(false);
    }
  };

  const handlePass = async () => {
    setPassing(true);
    setActionResult(null);
    
    try {
      const response = await fetchWithAuth(`http://localhost:5000/api/interactions/pass/${username}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        setActionResult({
          type: 'pass',
          message: `👋 Passed on ${profile.first_name}`
        });
        
        // Auto-redirect after 1 second
        setTimeout(() => {
          navigate('/discover');
        }, 1000);
      } else {
        throw new Error('Failed to pass');
      }
    } catch (err) {
      console.error('Error passing user:', err);
      // Still redirect even if API fails (offline fallback)
      navigate('/discover');
    } finally {
      setPassing(false);
    }
  };

  const handleGoBack = () => {
    navigate(-1); // Go back to previous page
  };

  const nextImage = () => {
    if (profile?.images && profile.images.length > 0) {
      setCurrentImageIndex((prev) => 
        prev === profile.images.length - 1 ? 0 : prev + 1
      );
    }
  };

  const prevImage = () => {
    if (profile?.images && profile.images.length > 0) {
      setCurrentImageIndex((prev) => 
        prev === 0 ? profile.images.length - 1 : prev - 1
      );
    }
  };

  const getImageUrl = (imagePath) => {
    if (!imagePath) return null;
    
    // Handle object format (with image_id and image_url)
    if (typeof imagePath === 'object' && imagePath.image_url) {
      imagePath = imagePath.image_url;
    }
    
    if (imagePath.startsWith('http')) return imagePath;
    
    // Handle relative paths
    const cleanPath = imagePath.replace(/^\/+/, '');
    return `http://localhost:5000/${cleanPath}`;
  };

  if (loading) {
    return (
      <div className="user-profile-loading">
        <div className="loading-spinner"></div>
        <p>Loading profile...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="user-profile-error">
        <div className="error-content">
          <h2>😔 Profile Unavailable</h2>
          <p>{error}</p>
          <div className="error-actions">
            <button onClick={handleGoBack} className="back-btn">
              ← Go Back
            </button>
            <button onClick={() => navigate('/discover')} className="discover-btn">
              🔍 Discover More
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="user-profile-error">
        <div className="error-content">
          <h2>Profile not found</h2>
          <button onClick={handleGoBack} className="back-btn">← Go Back</button>
        </div>
      </div>
    );
  }

  const images = profile.images || [];
  const displayImages = images.length > 0 ? images : [profile.profile_picture].filter(Boolean);
  const currentImage = displayImages[currentImageIndex];

  return (
    <div className="user-profile-view">
      {/* Header with back button */}
      <div className="profile-header">
        <button onClick={handleGoBack} className="back-button">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 12H5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M12 19L5 12L12 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Back
        </button>
        <h1>Profile</h1>
        <div></div> {/* Spacer for centering */}
      </div>

      {/* Main Profile Content */}
      <div className="profile-content">
        {/* Photo Gallery */}
        <div className="photo-gallery">
          {currentImage ? (
            <>
              <img 
                src={getImageUrl(currentImage)} 
                alt={`${profile.first_name}'s photo`}
                className="main-photo"
                onError={(e) => {
                  e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjQwMCIgdmlld0JveD0iMCAwIDQwMCA0MDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI0MDAiIGhlaWdodD0iNDAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxjaXJjbGUgY3g9IjIwMCIgY3k9IjE1MCIgcj0iNzAiIGZpbGw9IiNENUQ5REYiLz4KPHBhdGggZD0iTTEwMCAzMDBDMTAwIDI1MS44IDEzOCAyMTAgMTkwIDIxMEgyMTBDMjYyIDIxMCAzMDAgMjUxLjggMzAwIDMwMFYzMDBIMTAwVjMwMFoiIGZpbGw9IiNENUQ5REYiLz4KPC9zdmc+';
                }}
              />
              
              {/* Photo Navigation */}
              {displayImages.length > 1 && (
                <>
                  <button className="photo-nav prev" onClick={prevImage}>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M15 18L9 12L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </button>
                  <button className="photo-nav next" onClick={nextImage}>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M9 18L15 12L9 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </button>
                  
                  {/* Photo indicators */}
                  <div className="photo-indicators">
                    {displayImages.map((_, index) => (
                      <div 
                        key={index} 
                        className={`indicator ${index === currentImageIndex ? 'active' : ''}`}
                        onClick={() => setCurrentImageIndex(index)}
                      />
                    ))}
                  </div>
                </>
              )}
            </>
          ) : (
            <div className="no-photo">
              <svg width="100" height="100" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="200" height="200" fill="#F3F4F6"/>
                <circle cx="100" cy="75" r="35" fill="#D5D9DF"/>
                <path d="M50 150C50 125.9 69 105 95 105H105C131 105 150 125.9 150 150V150H50V150Z" fill="#D5D9DF"/>
              </svg>
              <p>No photos available</p>
            </div>
          )}
        </div>

        {/* Profile Information */}
        <div className="profile-info">
          <div className="basic-info">
            <h2 className="name">
              {profile.first_name} {profile.last_name}
              {profile.age && <span className="age">, {calculateAge(profile.birthdate)}</span>}
            </h2>
            
            {(profile.city || profile.country) && (
              <div className="location">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 10C21 17 12 23 12 23S3 17 3 10C3 5.02944 7.02944 1 12 1C16.9706 1 21 5.02944 21 10Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <circle cx="12" cy="10" r="3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                {profile.city && profile.country ? `${profile.city}, ${profile.country}` : (profile.city || profile.country)}
              </div>
            )}

            {profile.gender && (
              <div className="gender">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                  <path d="M8 12L16 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
                {profile.gender}
              </div>
            )}

            {profile.fame_rating && (
              <div className="fame-rating">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26" fill="currentColor"/>
                </svg>
                Fame Rating: {profile.fame_rating}/100
              </div>
            )}
          </div>

          {/* Bio */}
          {profile.bio && (
            <div className="bio-section">
              <h3>About {profile.first_name}</h3>
              <p className="bio-text">{profile.bio}</p>
            </div>
          )}

          {/* Interests */}
          {profile.interests && profile.interests.length > 0 && (
            <div className="interests-section">
              <h3>Interests</h3>
              <div className="interests-grid">
                {profile.interests.map((interest, index) => (
                  <span key={index} className="interest-tag">
                    {interest}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Action Result Display */}
        {actionResult && (
          <div className={`action-result ${actionResult.type}`}>
            <p>{actionResult.message}</p>
            {actionResult.type === 'match' && (
              <button 
                onClick={() => navigate('/chat')} 
                className="chat-now-btn"
              >
                💬 Chat Now
              </button>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="action-buttons">
          <button 
            className="pass-btn" 
            onClick={handlePass}
            disabled={passing || liking || actionResult}
          >
            {passing ? (
              <div className="button-spinner"></div>
            ) : (
              <>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                  <path d="M15 9L9 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M9 9L15 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                Pass
              </>
            )}
          </button>

          <button 
            className="like-btn" 
            onClick={handleLike}
            disabled={liking || passing || actionResult}
          >
            {liking ? (
              <div className="button-spinner"></div>
            ) : (
              <>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M20.84 4.61C20.3292 4.099 19.7228 3.69364 19.0554 3.41708C18.3879 3.14052 17.6725 2.99817 16.95 2.99817C16.2275 2.99817 15.5121 3.14052 14.8446 3.41708C14.1772 3.69364 13.5708 4.099 13.06 4.61L12 5.67L10.94 4.61C9.9083 3.5783 8.50903 2.9987 7.05 2.9987C5.59096 2.9987 4.19169 3.5783 3.16 4.61C2.1283 5.6417 1.5487 7.041 1.5487 8.5C1.5487 9.959 2.1283 11.3583 3.16 12.39L12 21.23L20.84 12.39C21.351 11.8792 21.7563 11.2728 22.0329 10.6053C22.3095 9.93789 22.4518 9.2225 22.4518 8.5C22.4518 7.7775 22.3095 7.0621 22.0329 6.39464C21.7563 5.72718 21.351 5.1208 20.84 4.61V4.61Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                Like
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserProfileView;