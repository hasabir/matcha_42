import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchWithAuth, api } from '../utils/api';
import { useNotifications } from '../contexts/NotificationContext';
import './UserProfileView.css';

const UserProfileView = () => {
  const { username } = useParams();
  const navigate = useNavigate();
  const { socket } = useNotifications();
  
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [liking, setLiking] = useState(false);
  const [passing, setPassing] = useState(false);
  const [actionResult, setActionResult] = useState(null);
  const [isMatched, setIsMatched] = useState(false);
  const [hasLiked, setHasLiked] = useState(false);
  const [unliking, setUnliking] = useState(false);
  const [userStatus, setUserStatus] = useState({ is_online: false, last_seen: null });
  const [blocking, setBlocking] = useState(false);
  const [reporting, setReporting] = useState(false);
  const [showActionMenu, setShowActionMenu] = useState(false);
  const [currentUserProfile, setCurrentUserProfile] = useState(null);
  const [hasProfilePicture, setHasProfilePicture] = useState(false);

  // Fetch current user's profile to check if they have a profile picture
  useEffect(() => {
    const fetchCurrentUserProfile = async () => {
      try {
        const response = await api.myProfilePic();
        if (response.ok) {
          const data = await response.json();
          const hasPic = data.result && data.result !== null;
          setHasProfilePicture(hasPic);
        }
      } catch (err) {
        console.error('Error fetching current user profile picture:', err);
        setHasProfilePicture(false);
      }
    };
    
    fetchCurrentUserProfile();
  }, []);

  useEffect(() => {
    if (!username) return;
    
    fetchUserProfile();
    // No need to call checkIfMatched() and checkIfLiked() separately anymore
    // They are now included in the profile response via interaction_status
    
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [username]); // Only re-run when username changes

  // Listen for real-time user status changes
  useEffect(() => {
    if (!socket || !profile) return;

    const handleStatusChange = (data) => {
      console.log(`📡 [UserProfileView] Received status change:`, data);
      console.log(`📡 [UserProfileView] Current profile user_id: ${profile.user_id}, profile.id: ${profile.id}`);
      
      // Only update if it's the profile we're viewing
      // Check all possible user_id fields
      const profileUserId = profile.user_id || profile.id;
      
      if (data.user_id === profileUserId) {
        console.log(`✅ [UserProfileView] Status change matches current profile! Updating to: ${data.is_online ? 'online' : 'offline'}`);
        setUserStatus({
          is_online: data.is_online,
          last_seen: data.last_seen
        });
        
        // Also update profile's interaction_status if it exists
        if (profile.interaction_status) {
          setProfile(prev => ({
            ...prev,
            interaction_status: {
              ...prev.interaction_status,
              is_online: data.is_online
            },
            last_seen: data.last_seen
          }));
        }
      } else {
        console.log(`⏭️ [UserProfileView] Status change is for different user (${data.user_id}), ignoring`);
      }
    };

    console.log(`🎧 [UserProfileView] Setting up status change listener for profile:`, profile.username);
    socket.on('user_status_changed', handleStatusChange);

    return () => {
      console.log(`🔇 [UserProfileView] Removing status change listener`);
      socket.off('user_status_changed', handleStatusChange);
    };
  }, [socket, profile]);

  const checkIfMatched = async () => {
    try {
      const response = await fetchWithAuth(`http://localhost:5000/api/interactions/is_matched`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ other_user: username })
      });
      if (response.ok) {
        const data = await response.json();
        setIsMatched(data.result === true);
      }
    } catch (err) {
      console.error('Error checking match status:', err);
    }
  };

  const checkIfLiked = async () => {
    try {
      const response = await fetchWithAuth(`http://localhost:5000/api/interactions/get_users/liked`);
      if (response.ok) {
        const data = await response.json();
        setHasLiked(data.result && data.result.includes(username));
      }
    } catch (err) {
      console.error('Error checking like status:', err);
    }
  };

  const fetchUserStatus = async () => {
    try {
      const response = await fetchWithAuth(`http://localhost:5000/api/profile/user_status/${username}`);
      if (response.ok) {
        const data = await response.json();
        setUserStatus(data.result || { is_online: false, last_seen: null });
      }
    } catch (err) {
      console.error('Error fetching user status:', err);
    }
  };

  const formatLastSeen = (lastSeenISO) => {
    if (!lastSeenISO) return 'Long time ago';
    
    const lastSeen = new Date(lastSeenISO);
    const now = new Date();
    const diffMs = now - lastSeen;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `Active ${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `Active ${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `Active ${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    return `Last seen ${lastSeen.toLocaleDateString()}`;
  };

  const handleBlock = async () => {
    if (!window.confirm(`Are you sure you want to block ${profile.first_name}? They will no longer be able to see your profile or contact you.`)) {
      return;
    }

    setBlocking(true);
    setActionResult(null);
    
    try {
      const response = await fetchWithAuth(`http://localhost:5000/api/interactions/block`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ blocked_user: username })
      });
      
      if (response.ok) {
        setActionResult({
          type: 'block',
          message: `🚫 You blocked ${profile.first_name}. They can no longer see your profile.`
        });
        
        // Redirect after 2 seconds
        setTimeout(() => {
          navigate('/discover');
        }, 2000);
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Failed to block user');
      }
    } catch (err) {
      console.error('Error blocking user:', err);
      setActionResult({
        type: 'error',
        message: `❌ ${err.message || 'Failed to block user. Please try again.'}`
      });
    } finally {
      setBlocking(false);
      setShowActionMenu(false);
    }
  };

  const handleReport = async () => {
    if (!window.confirm(`Are you sure you want to report ${profile.first_name} as a fake account?`)) {
      return;
    }

    setReporting(true);
    setActionResult(null);
    
    try {
      const response = await fetchWithAuth(`http://localhost:5000/api/interactions/report`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ reported_user: username })
      });
      
      if (response.ok) {
        setActionResult({
          type: 'report',
          message: `✅ Thank you for reporting ${profile.first_name}. We'll review this account.`
        });
        
        // Redirect after 2 seconds
        setTimeout(() => {
          navigate('/discover');
        }, 2000);
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Failed to report user');
      }
    } catch (err) {
      console.error('Error reporting user:', err);
      setActionResult({
        type: 'error',
        message: `❌ ${err.message || 'Failed to report user. Please try again.'}`
      });
    } finally {
      setReporting(false);
      setShowActionMenu(false);
    }
  };

  const fetchUserProfile = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // First, check if user is blocked to avoid 403 error in console
      const blockStatusResponse = await api.checkBlockStatus(username);
      if (blockStatusResponse.ok) {
        const blockStatus = await blockStatusResponse.json();
        if (blockStatus.is_blocked) {
          // User is blocked - show error without making profile request
          setError(blockStatus.message || 'You cannot view this profile. This user may have blocked you, or you may have blocked them.');
          setLoading(false);
          return;
        }
      }
      
      // User is not blocked, proceed with profile request
      const response = await fetchWithAuth(`http://localhost:5000/api/profile/get_profile/${username}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('User not found');
        }
        throw new Error('Failed to load profile');
      }
      
      const data = await response.json();
      const profileData = data.result || data;
      setProfile(profileData);
      
      // Use interaction_status from the profile response if available
      if (profileData.interaction_status) {
        setHasLiked(profileData.interaction_status.i_liked_them);
        setIsMatched(profileData.interaction_status.we_are_connected);
        
        // Update user status with online info from interaction_status
        setUserStatus({
          is_online: profileData.interaction_status.is_online,
          last_seen: profileData.last_seen
        });
      }
    } catch (err) {
      // Only log unexpected errors
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
    // Check if user has profile picture before allowing like
    if (!hasProfilePicture) {
      setActionResult({
        type: 'error',
        message: '📸 Please upload a profile picture before liking other users.'
      });
      return;
    }
    
    setLiking(true);
    setActionResult(null);
    
    try {
      const response = await fetchWithAuth(`http://localhost:5000/api/interactions/like/${username}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Like response:', data);
        
        setHasLiked(true);
        
        if (data.is_match || data.action === "match") {
          setIsMatched(true);
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
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Failed to send like');
      }
    } catch (err) {
      console.error('Error liking user:', err);
      setActionResult({
        type: 'error',
        message: `❌ ${err.message || 'Failed to send like. Please try again.'}`
      });
    } finally {
      setLiking(false);
    }
  };

  const handleUnlike = async () => {
    if (!window.confirm(`Are you sure you want to unlike ${profile.first_name}? This will remove your connection and delete your conversation history.`)) {
      return;
    }

    setUnliking(true);
    setActionResult(null);
    
    try {
      const response = await fetchWithAuth(`http://localhost:5000/api/interactions/unlike/${username}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Unlike response:', data);
        
        setHasLiked(false);
        
        if (data.was_matched) {
          setIsMatched(false);
          setActionResult({
            type: 'unlike',
            message: `💔 You unliked ${profile.first_name}. Your match and conversation have been removed.`
          });
        } else {
          setActionResult({
            type: 'unlike',
            message: `👋 You unliked ${profile.first_name}.`
          });
        }
        
        // Auto-redirect after 2 seconds
        setTimeout(() => {
          navigate('/discover');
        }, 2000);
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Failed to unlike');
      }
    } catch (err) {
      console.error('Error unliking user:', err);
      setActionResult({
        type: 'error',
        message: `❌ ${err.message || 'Failed to unlike. Please try again.'}`
      });
    } finally {
      setUnliking(false);
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

  // Compute total images count (profile pic + additional images, excluding duplicates)
  const getTotalImagesCount = () => {
    if (!profile) return 0;
    const images = profile.images || [];
    const profilePicUrl = profile.profile_picture;
    const additionalImageUrls = images
      .map(img => typeof img === 'string' ? img : img?.image_url)
      .filter(url => url && url !== profilePicUrl);
    return [profilePicUrl, ...additionalImageUrls].filter(Boolean).length;
  };

  const nextImage = () => {
    const totalImages = getTotalImagesCount();
    if (totalImages > 0) {
      setCurrentImageIndex((prev) => 
        prev === totalImages - 1 ? 0 : prev + 1
      );
    }
  };

  const prevImage = () => {
    const totalImages = getTotalImagesCount();
    if (totalImages > 0) {
      setCurrentImageIndex((prev) => 
        prev === 0 ? totalImages - 1 : prev - 1
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
  
  // Helper function to get image URL from either string or object format
  const getImageUrlFromItem = (img) => {
    if (!img) return null;
    return typeof img === 'string' ? img : img.image_url;
  };
  
  // Build display images: prioritize profile_picture first, then add other images
  // Remove duplicates by comparing URLs
  const profilePicUrl = profile.profile_picture;
  const additionalImageUrls = images
    .map(img => getImageUrlFromItem(img))
    .filter(url => url && url !== profilePicUrl); // Exclude duplicates of profile picture
  
  const displayImages = [profilePicUrl, ...additionalImageUrls].filter(Boolean);
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
        <div className="header-actions">
          {isMatched && (
            <span style={{ 
              background: 'linear-gradient(135deg, #28a745, #20c997)',
              color: 'white',
              padding: '8px 16px',
              borderRadius: '20px',
              fontSize: '14px',
              fontWeight: '600',
              marginRight: '10px'
            }}>
              ✨ Matched
            </span>
          )}
          
          {/* More options menu */}
          <div className="more-menu">
            <button 
              className="more-button"
              onClick={() => setShowActionMenu(!showActionMenu)}
              aria-label="More options"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="5" r="2" fill="currentColor"/>
                <circle cx="12" cy="12" r="2" fill="currentColor"/>
                <circle cx="12" cy="19" r="2" fill="currentColor"/>
              </svg>
            </button>
            
            {showActionMenu && (
              <div className="action-menu">
                <button 
                  onClick={handleBlock} 
                  disabled={blocking || reporting}
                  className="menu-item block-item"
                >
                  {blocking ? 'Blocking...' : '🚫 Block User'}
                </button>
                <button 
                  onClick={handleReport} 
                  disabled={blocking || reporting}
                  className="menu-item report-item"
                >
                  {reporting ? 'Reporting...' : '⚠️ Report as Fake'}
                </button>
              </div>
            )}
          </div>
        </div>
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
            
            {/* Online Status Indicator */}
            <div className="online-status">
              {userStatus.is_online ? (
                <span className="status-online">
                  <span className="status-dot online"></span>
                  Online now
                </span>
              ) : (
                <span className="status-offline">
                  <span className="status-dot offline"></span>
                  {formatLastSeen(userStatus.last_seen)}
                </span>
              )}
            </div>

            {/* Interaction Status Badges */}
            {profile.interaction_status && (
              <div className="interaction-badges">
                {profile.interaction_status.we_are_connected && (
                  <span className="badge badge-connected">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" fill="currentColor"/>
                    </svg>
                    Connected
                  </span>
                )}
                {profile.interaction_status.they_liked_me && !profile.interaction_status.we_are_connected && (
                  <span className="badge badge-liked-you">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" stroke="currentColor" strokeWidth="2"/>
                    </svg>
                    Likes You
                  </span>
                )}
                {profile.interaction_status.i_liked_them && !profile.interaction_status.we_are_connected && (
                  <span className="badge badge-you-liked">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <polyline points="20 6 9 17 4 12" stroke="currentColor" strokeWidth="2" fill="none"/>
                    </svg>
                    You Liked
                  </span>
                )}
              </div>
            )}
            
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
            disabled={passing || liking || unliking || actionResult}
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
            className="chat-btn" 
            onClick={() => {
              // Navigate to chat with userId query parameter
              const userId = profile?.user_id || profile?.id;
              if (userId) {
                navigate(`/chat?userId=${userId}`);
              } else {
                console.error('No user_id found in profile:', profile);
                navigate('/chat');
              }
            }}
            title="Send a message"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Chat
          </button>

          {hasLiked ? (
            <button 
              className={isMatched ? "disconnect-btn" : "unlike-btn"}
              onClick={handleUnlike}
              disabled={unliking || liking || passing || actionResult}
              title={isMatched ? "Disconnect from this match" : "Unlike this profile"}
            >
              {unliking ? (
                <div className="button-spinner"></div>
              ) : (
                <>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20.84 4.61C20.3292 4.099 19.7228 3.69364 19.0554 3.41708C18.3879 3.14052 17.6725 2.99817 16.95 2.99817C16.2275 2.99817 15.5121 3.14052 14.8446 3.41708C14.1772 3.69364 13.5708 4.099 13.06 4.61L12 5.67L10.94 4.61C9.9083 3.5783 8.50903 2.9987 7.05 2.9987C5.59096 2.9987 4.19169 3.5783 3.16 4.61C2.1283 5.6417 1.5487 7.041 1.5487 8.5C1.5487 9.959 2.1283 11.3583 3.16 12.39L12 21.23L20.84 12.39C21.351 11.8792 21.7563 11.2728 22.0329 10.6053C22.3095 9.93789 22.4518 9.2225 22.4518 8.5C22.4518 7.7775 22.3095 7.0621 22.0329 6.39464C21.7563 5.72718 21.351 5.1208 20.84 4.61V4.61Z" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M15 9L9 15M9 9L15 15" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  {isMatched ? 'Disconnect' : 'Unlike'}
                </>
              )}
            </button>
          ) : (
            <>
              <button 
                className="like-btn" 
                onClick={handleLike}
                disabled={liking || passing || unliking || actionResult || !hasProfilePicture}
                title={!hasProfilePicture ? "You need to add a profile picture before liking others" : "Like this profile"}
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
              {!hasProfilePicture && (
                <div className="profile-picture-warning">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="#f59e0b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  <span>Add a profile picture to like others</span>
                  <button 
                    className="add-picture-btn"
                    onClick={() => navigate('/my-profile')}
                  >
                    Add Picture
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserProfileView;