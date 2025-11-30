import React, { useState, useEffect } from 'react';
import { fetchWithAuth } from '../utils/api';
import './ProfileSuggestions.css';

// Toast notification component
const Toast = ({ message, type, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className={`toast toast-${type}`}>
      <span>{message}</span>
      <button onClick={onClose} className="toast-close">×</button>
    </div>
  );
};

const ProfileSuggestions = ({ currentUser }) => {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showFilters, setShowFilters] = useState(false);
  const [toasts, setToasts] = useState([]);
  const [likingUser, setLikingUser] = useState(null);
  
  // Filters state
  const [filters, setFilters] = useState({
    min_age: '',
    max_age: '',
    max_distance: 100, // Default: 100km for better relevance (was 500km)
    min_fame: '',
    max_fame: '',
    common_tags: '', // Added common tags filter
    sort_by: 'match_score',
    sort_order: 'desc'
  });

  const addToast = (message, type = 'success') => {
    // Check if the same message already exists to prevent duplicates
    setToasts(prev => {
      const exists = prev.some(toast => toast.message === message && toast.type === type);
      if (exists) {
        return prev; // Don't add duplicate
      }
      const id = Date.now();
      return [...prev, { id, message, type }];
    });
  };

  const removeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  useEffect(() => {
    loadSuggestions();
  }, []);

  const loadSuggestions = async () => {
    setLoading(true);
    try {
      // Build query parameters
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== '' && value !== null) {
          params.append(key, value);
        }
      });

      const response = await fetchWithAuth(`http://localhost:5000/api/browse/suggestions?${params}`);
      if (!response.ok) throw new Error('Failed to load suggestions');
      
      const data = await response.json();
      // Show top 20 suggestions for better browsing experience
      setSuggestions((data.suggestions || []).slice(0, 20));
      setError(null);
      
      if (data.suggestions && data.suggestions.length > 0) {
        addToast(`Found ${data.suggestions.length} matches! 🎉`, 'success');
      }
    } catch (err) {
      console.error('Error loading suggestions:', err);
      setError(err.message);
      addToast('Failed to load suggestions', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    // Allow empty values (user clearing the field)
    if (value === '' || value === null || value === undefined) {
      setFilters(prev => ({ ...prev, [key]: value }));
      return;
    }

    // Convert to number for validation
    const numValue = Number(value);
    
    // Validate filter inputs to prevent invalid values
    if (key === 'min_age') {
      if (numValue < 18 || numValue > 100) {
        // Don't show error while user is still typing (e.g., typing "5" to get "50")
        // Only validate if it looks like a complete number (2+ digits or clearly out of range)
        if (value.length >= 2 || numValue > 100) {
          addToast('Age must be between 18 and 100', 'error');
          return;
        }
      }
      // Check if min_age > max_age (only if max_age is set)
      if (filters.max_age && numValue > Number(filters.max_age)) {
        addToast('Minimum age cannot be greater than maximum age', 'error');
        return;
      }
    }
    
    if (key === 'max_age') {
      if (numValue < 18 || numValue > 100) {
        // Only validate if it looks like a complete number
        if (value.length >= 2 || numValue > 100) {
          addToast('Age must be between 18 and 100', 'error');
          return;
        }
      }
      // Check if max_age < min_age (only if min_age is set)
      if (filters.min_age && numValue < Number(filters.min_age)) {
        addToast('Maximum age cannot be less than minimum age', 'error');
        return;
      }
    }
    
    if (key === 'max_distance') {
      if (numValue < 0 || numValue > 10000) {
        addToast('Distance must be between 0 and 10000 km', 'error');
        return;
      }
    }
    
    if (key === 'min_fame') {
      if (numValue < 0 || numValue > 100) {
        addToast('Fame rating must be between 0 and 100', 'error');
        return;
      }
      // Check if min_fame > max_fame (only if max_fame is set)
      if (filters.max_fame && numValue > Number(filters.max_fame)) {
        addToast('Minimum fame cannot be greater than maximum fame', 'error');
        return;
      }
    }
    
    if (key === 'max_fame') {
      if (numValue < 0 || numValue > 100) {
        addToast('Fame rating must be between 0 and 100', 'error');
        return;
      }
      // Check if max_fame < min_fame (only if min_fame is set)
      if (filters.min_fame && numValue < Number(filters.min_fame)) {
        addToast('Maximum fame cannot be less than minimum fame', 'error');
        return;
      }
    }
    
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const applyFilters = () => {
    loadSuggestions();
  };

  const handleLike = async (username) => {
    // Check if user has profile picture before allowing like
    try {
      const profileCheckRes = await fetchWithAuth('http://localhost:5000/api/profile/me/profile-pic');
      if (profileCheckRes.ok) {
        const profileData = await profileCheckRes.json();
        if (!profileData.result || profileData.result === null) {
          addToast('📸 Please upload a profile picture before liking other users', 'error');
          return;
        }
      }
    } catch (err) {
      console.error('Error checking profile picture:', err);
    }
    
    setLikingUser(username);
    try {
      const response = await fetchWithAuth(`http://localhost:5000/api/interactions/like/${username}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Show appropriate toast based on action
        if (data.is_match) {
          addToast(`🎉 It's a Match with ${username}! You can now chat together!`, 'match');
        } else if (data.action === 'like') {
          addToast(`💖 You liked ${username}`, 'success');
        }
        
        // Remove user from suggestions with animation
        setTimeout(() => {
          setSuggestions(prev => prev.filter(s => s.username !== username));
        }, 500);
      } else {
        const errorData = await response.json();
        addToast(errorData.error || 'Failed to like user', 'error');
      }
    } catch (err) {
      console.error('Error liking user:', err);
      addToast('Network error. Please try again.', 'error');
    } finally {
      setLikingUser(null);
    }
  };

  const handlePass = async (username) => {
    // Simple animation and removal
    setSuggestions(prev => prev.filter(s => s.username !== username));
    addToast(`Passed on ${username}`, 'info');
  };

  const handleViewProfile = (username) => {
    window.open(`/profile/${username}`, '_blank');
  };

  return (
    <div className="profile-suggestions">
      {/* Toast notifications */}
      <div className="toast-container">
        {toasts.map(toast => (
          <Toast
            key={toast.id}
            message={toast.message}
            type={toast.type}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </div>

      <div className="suggestions-header">
        <div className="header-content">
          <h3>💫 Suggested Matches</h3>
          <p>People you might be interested in based on your preferences</p>
        </div>
        <div className="header-actions">
          <button 
            className="filters-toggle"
            onClick={() => setShowFilters(!showFilters)}
          >
            {showFilters ? '📋 Hide Filters' : '🔍 Filters'}
          </button>
          <button 
            className="view-all-btn"
            onClick={() => window.open('/discover', '_blank')}
          >
            View All
          </button>
        </div>
      </div>

      {/* GPS Location Warning Banner */}
      {currentUser && !currentUser.latitude && (
        <div className="info-banner warning-banner">
          <div className="info-icon">⚠️</div>
          <div className="info-content">
            <strong>Location not set!</strong>
            <p>Enable GPS in your profile settings for distance-based matching and to see users near you.</p>
          </div>
        </div>
      )}

      {/* Geographic Priority Info Banner */}
      <div className="info-banner geographical-priority-banner">
        <div className="info-icon">ℹ️</div>
        <div className="info-content">
          <strong>🌍 Geographical Priority System:</strong>
          <div className="priority-tiers">
            <span className="tier tier-0">🎯 Tier 1: Users within 50km (highest priority)</span>
            <span className="tier tier-1">📍 Tier 2: Same city or country</span>
            <span className="tier tier-2">🌐 Tier 3: Other locations</span>
          </div>
          <small>Results are automatically sorted by geographical proximity, then by your selected criteria.</small>
        </div>
      </div>

      {/* Enhanced Filters */}
      {showFilters && (
        <div className="enhanced-filters">
          <div className="filters-grid">
            {/* Age Filter */}
            <div className="filter-section">
              <h4>🎂 Age Range</h4>
              <div className="age-range">
                <input
                  type="number"
                  placeholder="Min age"
                  value={filters.min_age}
                  onChange={(e) => handleFilterChange('min_age', e.target.value)}
                  min="18"
                  max="100"
                />
                <span>to</span>
                <input
                  type="number"
                  placeholder="Max age"
                  value={filters.max_age}
                  onChange={(e) => handleFilterChange('max_age', e.target.value)}
                  min="18"
                  max="100"
                />
              </div>
            </div>

            {/* Distance Filter */}
            <div className="filter-section">
              <h4>📍 Distance: {filters.max_distance ? `${filters.max_distance}km` : 'All'}</h4>
              <input
                type="range"
                min="1"
                max="500"
                value={filters.max_distance || 100}
                onChange={(e) => handleFilterChange('max_distance', e.target.value)}
                className="distance-slider"
              />
              <div className="distance-labels">
                <span>1km</span>
                <span>500km</span>
              </div>
            </div>

            {/* Fame Rating Filter */}
            <div className="filter-section">
              <h4>⭐ Fame Rating</h4>
              <div className="fame-range">
                <input
                  type="number"
                  placeholder="Min fame"
                  value={filters.min_fame}
                  onChange={(e) => handleFilterChange('min_fame', e.target.value)}
                  min="0"
                  max="100"
                />
                <span>to</span>
                <input
                  type="number"
                  placeholder="Max fame"
                  value={filters.max_fame}
                  onChange={(e) => handleFilterChange('max_fame', e.target.value)}
                  min="0"
                  max="100"
                />
              </div>
            </div>

            {/* Common Tags Filter */}
            <div className="filter-section">
              <h4>🏷️ Common Interests</h4>
              <input
                type="text"
                placeholder="e.g., music, travel, sports"
                value={filters.common_tags}
                onChange={(e) => handleFilterChange('common_tags', e.target.value)}
                className="tags-input"
              />
              <small>Separate with commas</small>
            </div>

            {/* Sort Options */}
            <div className="filter-section">
              <h4>📊 Sort By</h4>
              <select
                value={filters.sort_by}
                onChange={(e) => handleFilterChange('sort_by', e.target.value)}
                className="sort-select"
              >
                <option value="match_score">🎯 Best Match</option>
                <option value="distance">📍 Distance</option>
                <option value="age">🎂 Age</option>
                <option value="fame_rating">⭐ Fame Rating</option>
                <option value="common_tags">🏷️ Common Interests</option>
                <option value="city">🏙️ City</option>
                <option value="country">🌍 Country</option>
              </select>
              
              <div className="sort-order">
                <label>
                  <input
                    type="radio"
                    name="sort_order"
                    value="desc"
                    checked={filters.sort_order === 'desc'}
                    onChange={(e) => handleFilterChange('sort_order', e.target.value)}
                  />
                  Descending
                </label>
                <label>
                  <input
                    type="radio"
                    name="sort_order"
                    value="asc"
                    checked={filters.sort_order === 'asc'}
                    onChange={(e) => handleFilterChange('sort_order', e.target.value)}
                  />
                  Ascending
                </label>
              </div>
            </div>
          </div>
          
          <div className="filter-actions">
            <button className="apply-btn" onClick={applyFilters}>
              🔍 Apply Filters
            </button>
            <button 
              className="reset-btn" 
              onClick={() => {
                setFilters({
                  min_age: '',
                  max_age: '',
                  max_distance: 100,
                  min_fame: '',
                  max_fame: '',
                  common_tags: '',
                  sort_by: 'match_score',
                  sort_order: 'desc'
                });
                setTimeout(loadSuggestions, 100);
              }}
            >
              🔄 Reset
            </button>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="suggestions-loading">
          <div className="loading-spinner"></div>
          <p>Finding your perfect matches...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="suggestions-error">
          <p>❌ {error}</p>
          <button onClick={loadSuggestions}>Try Again</button>
        </div>
      )}

      {/* Suggestions Grid */}
      {!loading && !error && (
        <div className="suggestions-grid">
          {suggestions.length === 0 ? (
            <div className="no-suggestions">
              <div className="no-suggestions-content">
                <h4>🔍 No matches found</h4>
                <p>Try expanding your search criteria or check back later!</p>
                <button 
                  onClick={() => {
                    setFilters(prev => ({ ...prev, max_distance: 500, min_age: '', max_age: '' }));
                    setTimeout(loadSuggestions, 100);
                  }}
                >
                  Expand Search
                </button>
              </div>
            </div>
          ) : (
            suggestions.map((person) => (
              <div key={person.username} className="suggestion-card">
                {/* Profile Image */}
                <div className="suggestion-image">
                  {person.profile_picture ? (
                    <img 
                      src={person.profile_picture} 
                      alt={`${person.first_name || 'User'}'s profile`}
                      onError={(e) => {
                        e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxjaXJjbGUgY3g9IjEwMCIgY3k9Ijc1IiByPSIzNSIgZmlsbD0iI0Q1RDlERiIvPgo8cGF0aCBkPSJNNTAgMTUwQzUwIDEyNS45IDY5IDEwNSA5NSAxMDVIMTA1QzEzMSAxMDUgMTUwIDEyNS45IDE1MCAxNTBWMTUwSDUwVjE1MFoiIGZpbGw9IiNENUQ5REYiLz4KPC9zdmc+';
                      }}
                    />
                  ) : (
                    <div className="placeholder-image">
                      <span>👤</span>
                    </div>
                  )}

                  {/* Match Score Badge */}
                  <div className="match-score-badge">
                    {Math.round(person.match_score || 0)}% Match
                  </div>

                  {/* Online Status (mock) */}
                  <div className="online-indicator"></div>
                </div>

                {/* Card Content */}
                <div className="suggestion-content">
                  <div className="suggestion-header">
                    <h4>{person.first_name || 'Anonymous'} {person.last_name || ''}</h4>
                    {person.age && <span className="age">🎂 {person.age}</span>}
                  </div>

                  <div className="suggestion-details">
                    {/* Geographic Area Priority Display */}
                    <div className="detail-item location-priority">
                      <span className="detail-icon">📍</span>
                      <span className="detail-text">
                        {person.distance ? (
                          <span className={person.distance < 10 ? 'very-close' : person.distance < 50 ? 'same-area' : 'distant'}>
                            {person.distance}km away
                          </span>
                        ) : (
                          <span className="no-location">
                            {person.city ? `${person.city}${person.country ? `, ${person.country}` : ''}` : 'Location not set'}
                          </span>
                        )}
                      </span>
                    </div>

                    {/* Fame Rating Display */}
                    <div className="detail-item fame-rating">
                      <span className="detail-icon">⭐</span>
                      <span className="detail-text">
                        <span className={`fame-score ${person.fame_rating >= 80 ? 'high' : person.fame_rating >= 50 ? 'medium' : 'low'}`}>
                          Fame: {person.fame_rating || 0}/100
                        </span>
                      </span>
                    </div>

                    {/* Common Interests Display */}
                    <div className="detail-item common-interests">
                      <span className="detail-icon">🤝</span>
                      <span className="detail-text">
                        {person.common_interests > 0 ? (
                          <span className={`interests-count ${person.common_interests >= 5 ? 'very-compatible' : person.common_interests >= 3 ? 'compatible' : 'some-match'}`}>
                            {person.common_interests} shared interest{person.common_interests !== 1 ? 's' : ''}
                          </span>
                        ) : (
                          <span className="no-interests">No shared interests yet</span>
                        )}
                      </span>
                    </div>

                    {/* Match Score Indicator */}
                    <div className="detail-item match-indicator">
                      <span className="detail-icon">🎯</span>
                      <span className="detail-text">
                        <span className={`match-percentage ${person.match_score >= 80 ? 'excellent' : person.match_score >= 60 ? 'good' : 'fair'}`}>
                          {Math.round(person.match_score || 0)}% compatibility
                        </span>
                      </span>
                    </div>
                  </div>

                  {/* Interests Preview */}
                  {person.interests && person.interests.length > 0 && (
                    <div className="interests-preview">
                      {person.interests.slice(0, 3).map((interest, idx) => (
                        <span key={idx} className="interest-chip">{interest}</span>
                      ))}
                      {person.interests.length > 3 && (
                        <span className="more-interests">+{person.interests.length - 3}</span>
                      )}
                    </div>
                  )}

                  {/* Compatibility Reasons */}
                  {person.compatibility_reasons && person.compatibility_reasons.length > 0 && (
                    <div className="compatibility-preview">
                      <div className="compatibility-reason">
                        ✨ {person.compatibility_reasons[0]}
                      </div>
                    </div>
                  )}

                  {/* Bio Preview */}
                  {person.bio && (
                    <div className="bio-snippet">
                      "{person.bio.length > 60 ? `${person.bio.substring(0, 60)}...` : person.bio}"
                    </div>
                  )}
                </div>

                {/* Card Actions */}
                <div className="suggestion-actions">
                  <button 
                    className={`action-btn like-btn ${likingUser === person.username ? 'liking' : ''}`}
                    onClick={() => handleLike(person.username)}
                    title="Like this profile"
                    disabled={likingUser === person.username}
                  >
                    {likingUser === person.username ? (
                      <span className="spinner"></span>
                    ) : (
                      <>
                        <span>💖</span>
                        <span>Like</span>
                      </>
                    )}
                  </button>
                  <button 
                    className="action-btn view-btn"
                    onClick={() => handleViewProfile(person.username)}
                    title="View full profile"
                  >
                    <span>👤</span>
                    <span>Profile</span>
                  </button>
                  <button 
                    className="action-btn pass-btn"
                    onClick={() => handlePass(person.username)}
                    title="Pass on this profile"
                  >
                    <span>�</span>
                    <span>Pass</span>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Footer */}
      {!loading && !error && suggestions.length > 0 && (
        <div className="suggestions-footer">
          <button 
            className="refresh-btn"
            onClick={loadSuggestions}
          >
            🔄 Refresh Suggestions
          </button>
          <button 
            className="discover-more-btn"
            onClick={() => window.open('/discover', '_blank')}
          >
            🔍 Discover More People
          </button>
        </div>
      )}
    </div>
  );
};

export default ProfileSuggestions;