import React, { useState, useEffect, useCallback, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { fetchWithAuth, api, BASE } from "../utils/api";
import "./MyProfilePage.css";

const FALLBACK_AVATAR = "https://static-00.iconduck.com/assets.00/user-avatar-1024x1024-2xhpdo1n.png";
const API_BASE = process.env.REACT_APP_API_BASE || BASE;

// Helper function for absolute URLs
function toAbsoluteUrl(url) {
  if (!url) return FALLBACK_AVATAR;
  if (/^https?:\/\//i.test(url)) return url;

  try {
    let cleanUrl = url.replace(/^\/+/, "");
    if (cleanUrl.startsWith("profiles/") && !cleanUrl.startsWith("static/")) {
      cleanUrl = `static/${cleanUrl}`;
    }
    return `${API_BASE.replace(/\/+$/, "")}/${cleanUrl}`;
  } catch {
    return url.startsWith("/") ? `${API_BASE}${url}` : `${API_BASE}/${url}`;
  }
}

const MyProfilePage = () => {
  const navigate = useNavigate();
  
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState({
    views: 0,
    likes: 0,
    matches: 0
  });
  
  // Dashboard-specific state
  const [viewers, setViewers] = useState([]);
  const [likedUsers, setLikedUsers] = useState([]);
  const [likers, setLikers] = useState([]);
  
  // Photo upload state
  const [uploadingPhotos, setUploadingPhotos] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  
  // Stable image error handler
  const onImgError = useMemo(
    () => (e) => {
      if (e?.target?.src !== FALLBACK_AVATAR) {
        e.target.src = FALLBACK_AVATAR;
      }
    },
    []
  );

  // Memoize fetchMyProfile to prevent infinite loop
  const fetchMyProfile = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      console.log("Fetching user profile info...");
      
      // Get basic user info using fetchWithAuth for proper token handling
      const userResponse = await fetchWithAuth("http://localhost:5000/api/profile/my_profile");

      if (!userResponse.ok) {
        const errorData = await userResponse.json().catch(() => ({}));
        console.error("Failed to fetch user info:", errorData);
        
        if (userResponse.status === 401 || userResponse.status === 403) {
          // fetchWithAuth should have already handled this, but just in case
          console.log("Authentication failed, redirecting to signin");
          navigate("/signin", { replace: true });
          return;
        }
        
        throw new Error(errorData.error || `HTTP ${userResponse.status}: Failed to fetch user info`);
      }

      const userData = await userResponse.json();
      console.log("User data received:", userData);
      
      // If no profile exists, redirect to setup
      if (!userData.has_profile) {
        console.log("No profile found, redirecting to profile setup");
        navigate("/profile-step-one", { replace: true });
        return;
      }

      // Get full profile data using "me" which is more efficient
      console.log("Fetching full profile data...");
      const profileResponse = await fetchWithAuth("http://localhost:5000/api/profile/get_profile/me");

      if (!profileResponse.ok) {
        const errorData = await profileResponse.json().catch(() => ({}));
        console.error("Failed to fetch profile:", errorData);
        throw new Error(errorData.error || `HTTP ${profileResponse.status}: Failed to fetch profile`);
      }

      const profileData = await profileResponse.json();
      console.log("Profile data received:", profileData);
      
      // Handle different response formats
      if (profileData.result) {
        setProfile(profileData.result);
      } else if (profileData.error) {
        throw new Error(profileData.error);
      } else {
        // Assume the whole response is the profile data
        setProfile(profileData);
      }
      
    } catch (err) {
      console.error("Error in fetchMyProfile:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  // Enhanced fetchStats that also gets dashboard data
  const fetchStats = useCallback(async () => {
    try {
      console.log("Fetching profile statistics and dashboard data...");

      // Fetch all stats in parallel using fetchWithAuth
      const [viewsResponse, likesResponse, matchesResponse] = await Promise.all([
        fetchWithAuth("http://localhost:5000/api/profile/get_profile_vistors"),
        fetchWithAuth("http://localhost:5000/api/interactions/who_liked_me"),
        fetchWithAuth("http://localhost:5000/api/interactions/my_connections")
      ]);

      // Process responses
      const newStats = {
        views: 0,
        likes: 0,
        matches: 0
      };

      // Handle views and viewers
      if (viewsResponse.ok) {
        const viewsData = await viewsResponse.json();
        const visitorsData = viewsData.result || [];
        newStats.views = visitorsData.length;
        
        // Get visitors with profile pictures (limited to 12 for display)
        if (visitorsData.length > 0) {
          const viewersWithPics = await Promise.all(
            visitorsData.slice(0, 12).map(async (visitor) => {
              try {
                const picRes = await api.userProfilePic(visitor.username);
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
          setViewers(viewersWithPics);
        }
        console.log("Views:", newStats.views);
      }

      // Handle likes (people who liked me)
      if (likesResponse.ok) {
        const likesData = await likesResponse.json();
        const likersData = likesData || [];
        newStats.likes = likersData.length;
        
        // Get likers with details (limited to 16 for display)
        if (likersData.length > 0) {
          const likersWithDetails = await Promise.all(
            likersData.slice(0, 16).map(async (username) => {
              try {
                const [matchRes, picRes] = await Promise.all([
                  api.isMatched(username),
                  api.userProfilePic(username)
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
          setLikers(likersWithDetails);
        }
        console.log("Likes:", newStats.likes);
      }

      // Handle matches  
      if (matchesResponse.ok) {
        const matchesData = await matchesResponse.json();
        newStats.matches = matchesData.length || 0;
        console.log("Matches:", newStats.matches);
      }

      // Also fetch users I liked
      try {
        const likedRes = await api.getUsers("liked");
        const likedData = await likedRes.json();

        if (likedRes.ok && Array.isArray(likedData.result)) {
          const likedWithDetails = await Promise.all(
            likedData.result.slice(0, 16).map(async (username) => {
              try {
                const [matchRes, picRes] = await Promise.all([
                  api.isMatched(username),
                  api.userProfilePic(username)
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
          setLikedUsers(likedWithDetails);
        }
      } catch (err) {
        console.error("Failed to load liked users:", err);
      }

      console.log("Final stats:", newStats);
      setStats(newStats);
    } catch (err) {
      console.error("Error fetching stats:", err);
      // Don't fail the whole page if stats fail
      setStats({
        views: 0,
        likes: 0,
        matches: 0
      });
    }
  }, []);

  // Effect runs only once on mount
  useEffect(() => {
    fetchMyProfile();
    fetchStats();
  }, [fetchMyProfile, fetchStats]);

  // Separate useEffect to handle navigation if needed
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/login", { replace: true });
    }
  }, [navigate]);

  // Refresh function for manual updates
  const refreshProfile = useCallback(async () => {
    setRefreshing(true);
    await Promise.all([fetchMyProfile(), fetchStats()]);
    setRefreshing(false);
  }, [fetchMyProfile, fetchStats]);

  // Listen for focus events to refresh data when user returns
  useEffect(() => {
    const handleFocus = () => {
      // Only refresh if we have a profile and it's been more than 30 seconds
      if (profile && document.visibilityState === 'visible') {
        refreshProfile();
      }
    };

    document.addEventListener('visibilitychange', handleFocus);
    window.addEventListener('focus', handleFocus);

    return () => {
      document.removeEventListener('visibilitychange', handleFocus);
      window.removeEventListener('focus', handleFocus);
    };
  }, [profile, refreshProfile]);

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
      <div className="my-profile-loading">
        <div className="spinner"></div>
        <p>Loading your profile...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="my-profile-error">
        <h2>Oops!</h2>
        <p>{error}</p>
        <button onClick={() => navigate("/dashboard")}>Back to Dashboard</button>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="my-profile-error">
        <h2>Profile not found</h2>
        <button onClick={() => navigate("/profile-step-one")}>Create Profile</button>
      </div>
    );
  }

  // Build images array with fallback
  const allImages = [
    profile?.profile_picture,
    ...(profile?.images || [])
  ].filter(Boolean);

  const displayName = profile?.first_name && profile?.last_name 
    ? `${profile.first_name} ${profile.last_name}` 
    : profile?.username || 'User';

  // Photo upload handler
  const handlePhotoUpload = async (e) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;
    
    // Check if adding these files would exceed the 5 photo limit
    const currentCount = allImages.length;
    const newCount = currentCount + files.length;
    
    if (newCount > 5) {
      setUploadStatus(`❌ Cannot upload ${files.length} photos. You can only have 5 photos maximum. Current: ${currentCount}`);
      setTimeout(() => setUploadStatus(null), 5000);
      return;
    }

    try {
      setUploadingPhotos(true);
      setUploadStatus("📤 Uploading photos...");
      
      const formData = new FormData();
      files.forEach((file) => formData.append("images", file));
      
      const response = await fetchWithAuth("http://localhost:5000/api/profile/upload_images", {
        method: "POST",
        body: formData,
      });
      
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data?.error || "Failed to upload photos");
      
      // Refresh profile to get updated images
      await fetchMyProfile();
      
      setUploadStatus(`✅ Successfully uploaded ${files.length} photo${files.length > 1 ? 's' : ''}!`);
      setTimeout(() => setUploadStatus(null), 3000);
      
      // Clear the file input
      e.target.value = '';
      
    } catch (error) {
      console.error("Photo upload error:", error);
      setUploadStatus(`❌ Failed to upload photos: ${error.message}`);
      setTimeout(() => setUploadStatus(null), 5000);
    } finally {
      setUploadingPhotos(false);
    }
  };

  // Photo delete handler
  const handleDeletePhoto = async (photoPath) => {
    if (!photoPath) return;
    
    const confirmDelete = window.confirm("Are you sure you want to delete this photo?");
    if (!confirmDelete) return;

    try {
      setUploadStatus("🗑️ Deleting photo...");
      
      const response = await fetchWithAuth("http://localhost:5000/api/profile/delete_image", {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ image_path: photoPath }),
      });
      
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data?.error || "Failed to delete photo");
      }
      
      // Refresh profile to get updated images
      await fetchMyProfile();
      
      setUploadStatus("✅ Photo deleted successfully!");
      setTimeout(() => setUploadStatus(null), 3000);
      
    } catch (error) {
      console.error("Photo delete error:", error);
      setUploadStatus(`❌ Failed to delete photo: ${error.message}`);
      setTimeout(() => setUploadStatus(null), 5000);
    }
  };

  return (
    <div className="dashboard-container">
      {/* Enhanced Profile Header */}
      <div className="profile-header">
        <div 
          className="profile-pic"
          onClick={() => navigate("/settings")}
          style={{ cursor: "pointer" }}
        >
          <img 
            src={allImages.length > 0 ? toAbsoluteUrl(allImages[0]) : FALLBACK_AVATAR} 
            alt="Profile" 
            onError={onImgError} 
          />
          <span className="profile-label">Profile</span>
        </div>
        <h1 className="welcome-text">Welcome back, {displayName}!</h1>
        <p className="fame-rating">Fame rating: {profile?.fame_rating || 5}</p>
        
        <div className="header-actions">
          <button 
            className="refresh-btn-header" 
            onClick={refreshProfile}
            disabled={refreshing}
            title="Refresh profile data"
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2"
              className={refreshing ? 'spinning' : ''}
            >
              <polyline points="23 4 23 10 17 10"></polyline>
              <polyline points="1 20 1 14 7 14"></polyline>
              <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"></path>
            </svg>
            {refreshing ? 'Updating...' : 'Refresh'}
          </button>
          <button className="edit-btn-header" onClick={() => navigate("/settings")}>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
            Edit Profile
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-container">
        <div className="stat-card">
          <h3>Profile Views</h3>
          <p className="stat-number">{stats.views}</p>
        </div>
        <div className="stat-card">
          <h3>Likes Received</h3>
          <p className="stat-number">{stats.likes}</p>
        </div>
        <div className="stat-card">
          <h3>Matches</h3>
          <p className="stat-number">{stats.matches}</p>
        </div>
      </div>

      {/* Profile Info Section */}
      <div className="dashboard-section">
        <div className="section-header">
          <h2>Profile Details</h2>
          <button className="view-all-btn" onClick={() => navigate("/settings")}>
            Edit Profile
          </button>
        </div>
        
        <div className="profile-info-card">
          <div className="profile-details-grid">
            <div className="detail-card">
              <div className="detail-icon">👤</div>
              <div className="detail-content">
                <span className="detail-label">Name</span>
                <span className="detail-value">{displayName}</span>
              </div>
            </div>
            
            {profile?.age && (
              <div className="detail-card">
                <div className="detail-icon">🎂</div>
                <div className="detail-content">
                  <span className="detail-label">Age</span>
                  <span className="detail-value">{calculateAge(profile.birthdate)} years old</span>
                </div>
              </div>
            )}
            
            {profile?.gender && (
              <div className="detail-card">
                <div className="detail-icon">⚧</div>
                <div className="detail-content">
                  <span className="detail-label">Gender</span>
                  <span className="detail-value">{profile.gender}</span>
                </div>
              </div>
            )}
            
            {(profile?.city || profile?.country) && (
              <div className="detail-card">
                <div className="detail-icon">📍</div>
                <div className="detail-content">
                  <span className="detail-label">Location</span>
                  <span className="detail-value">{profile?.city || 'Unknown'}, {profile?.country || 'Unknown'}</span>
                </div>
              </div>
            )}

            <div className="photo-gallery-card">
              <div className="photo-gallery-header">
                <div className="gallery-title">
                  <div className="detail-icon">📸</div>
                  <div>
                    <span className="detail-label">My Photos</span>
                    <span className="photo-count-text">{allImages.length}/5 photos</span>
                  </div>
                </div>
                <button 
                  className="add-photo-btn"
                  onClick={() => document.getElementById('photo-upload').click()}
                  disabled={allImages.length >= 5 || uploadingPhotos}
                >
                  {uploadingPhotos ? "Uploading..." : "+ Add Photo"}
                </button>
              </div>

              <div className="photo-grid">
                {allImages.map((img, index) => (
                  <div key={index} className="photo-item">
                    <img 
                      src={toAbsoluteUrl(img)} 
                      alt={`Photo ${index + 1}`}
                      onError={onImgError}
                    />
                    <div className="photo-overlay">
                      <button 
                        className="delete-photo-btn"
                        onClick={() => handleDeletePhoto(img)}
                        title="Delete photo"
                      >
                        ✕
                      </button>
                    </div>
                    {index === 0 && (
                      <div className="main-photo-badge">Main</div>
                    )}
                  </div>
                ))}
                
                {/* Empty slots for remaining photos */}
                {Array.from({ length: Math.max(0, 5 - allImages.length) }).map((_, index) => (
                  <div 
                    key={`empty-${index}`} 
                    className="photo-placeholder"
                    onClick={() => document.getElementById('photo-upload').click()}
                  >
                    <div className="placeholder-content">
                      <div className="placeholder-icon">📷</div>
                      <span>Add Photo</span>
                    </div>
                  </div>
                ))}
              </div>

              <input
                id="photo-upload"
                type="file"
                accept="image/*"
                multiple
                style={{ display: 'none' }}
                onChange={handlePhotoUpload}
              />

              {uploadStatus && (
                <div className={`upload-status ${uploadStatus.includes('✅') ? 'success' : 'error'}`}>
                  {uploadStatus}
                </div>
              )}
            </div>

            {profile?.bio && (
              <div className="detail-card bio-card">
                <div className="detail-icon">💭</div>
                <div className="detail-content">
                  <span className="detail-label">About Me</span>
                  <p className="bio-text">{profile.bio}</p>
                </div>
              </div>
            )}
          </div>
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
            viewers.map((viewer, index) => (
              <div
                key={`${viewer.username}-${index}`}
                className="user-card"
                onClick={() => navigate(`/profile/${viewer.username}`)}
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
            likedUsers.map((u, index) => (
              <div
                key={`${u.username}-${index}`}
                className="user-card"
                onClick={() => navigate(`/profile/${u.username}`)}
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
            likers.map((u, index) => (
              <div
                key={`${u.username}-${index}`}
                className="user-card"
                onClick={() => navigate(`/profile/${u.username}`)}
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
        <button className="action-btn" onClick={() => navigate("/discover")}>
          Discover New Matches
        </button>
      </div>
    </div>
  );
};

export default MyProfilePage;
