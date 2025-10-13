import React, { useState, useEffect } from 'react';
import { fetchWithAuth } from '../utils/api';
import './ProfileSuggestions.css';

const ProfileSuggestions = ({ currentUser }) => {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showFilters, setShowFilters] = useState(false);
  
  // Filters state
  const [filters, setFilters] = useState({
    min_age: '',
    max_age: '',
    max_distance: 50, // Default closer range for profile suggestions
    min_fame: '',
    max_fame: '',
    sort_by: 'match_score',
    sort_order: 'desc'
  });

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

      const response = await fetchWithAuth(`http://localhost:5555/api/browse/suggestions?${params}`);
      if (!response.ok) throw new Error('Failed to load suggestions');
      
      const data = await response.json();
      // Limit to top 6 suggestions for profile page
      setSuggestions((data.suggestions || []).slice(0, 6));
      setError(null);
    } catch (err) {
      console.error('Error loading suggestions:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const applyFilters = () => {
    loadSuggestions();
  };

  const handleLike = async (username) => {
    try {
      const response = await fetchWithAuth(`http://localhost:5555/api/interactions/like/${username}`, {
        method: 'POST'
      });
      if (response.ok) {
        const data = await response.json();
        if (data.match) {
          alert(`🎉 It's a match with ${username}!`);
        } else {
          alert(`💖 You liked ${username}`);
        }
        // Remove liked user from suggestions
        setSuggestions(prev => prev.filter(s => s.username !== username));
      }
    } catch (err) {
      console.error('Error liking user:', err);
    }
  };

  const handleViewProfile = (username) => {
    window.open(`/profile/${username}`, '_blank');
  };

  return (
    <div className="profile-suggestions">
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

      {/* Quick Filters */}
      {showFilters && (
        <div className="quick-filters">
          <div className="filter-row">
            <div className="filter-item">
              <label>Age Range:</label>
              <div className="age-range">
                <input
                  type="number"
                  placeholder="Min"
                  value={filters.min_age}
                  onChange={(e) => handleFilterChange('min_age', e.target.value)}
                  min="18"
                  max="100"
                />
                <span>-</span>
                <input
                  type="number"
                  placeholder="Max"
                  value={filters.max_age}
                  onChange={(e) => handleFilterChange('max_age', e.target.value)}
                  min="18"
                  max="100"
                />
              </div>
            </div>

            <div className="filter-item">
              <label>Distance: {filters.max_distance}km</label>
              <input
                type="range"
                min="5"
                max="200"
                value={filters.max_distance}
                onChange={(e) => handleFilterChange('max_distance', e.target.value)}
                className="distance-slider"
              />
            </div>

            <div className="filter-item">
              <label>Sort By:</label>
              <select
                value={filters.sort_by}
                onChange={(e) => handleFilterChange('sort_by', e.target.value)}
              >
                <option value="match_score">Best Match</option>
                <option value="distance">Distance</option>
                <option value="age">Age</option>
                <option value="fame_rating">Fame Rating</option>
                <option value="common_tags">Common Interests</option>
              </select>
            </div>

            <button className="apply-btn" onClick={applyFilters}>
              Apply
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
                    setFilters(prev => ({ ...prev, max_distance: 100, min_age: '', max_age: '' }));
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
                      alt={`${person.first_name}'s profile`}
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
                    <h4>{person.first_name} {person.last_name}</h4>
                    <span className="age">🎂 {person.age}</span>
                  </div>

                  <div className="suggestion-details">
                    <div className="detail-item">
                      <span className="detail-icon">📍</span>
                      <span className="detail-text">
                        {person.distance ? `${person.distance}km away` : person.city}
                      </span>
                    </div>

                    <div className="detail-item">
                      <span className="detail-icon">⭐</span>
                      <span className="detail-text">
                        Fame: {person.fame_rating}/100
                      </span>
                    </div>

                    {person.common_interests > 0 && (
                      <div className="detail-item">
                        <span className="detail-icon">🤝</span>
                        <span className="detail-text">
                          {person.common_interests} shared interests
                        </span>
                      </div>
                    )}
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
                    className="action-btn like-btn"
                    onClick={() => handleLike(person.username)}
                    title="Like this profile"
                  >
                    💖
                  </button>
                  <button 
                    className="action-btn view-btn"
                    onClick={() => handleViewProfile(person.username)}
                    title="View full profile"
                  >
                    👤
                  </button>
                  <button 
                    className="action-btn chat-btn"
                    onClick={() => window.open(`/chat/${person.username}`, '_blank')}
                    title="Send message"
                  >
                    💬
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