import React, { useState, useEffect } from 'react';
import { fetchWithAuth } from '../utils/api';
import './BrowsePage.css';

const BrowsePage = () => {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    min_age: '',
    max_age: '',
    max_distance: 100,
    min_fame: '',
    max_fame: '',
    sort_by: 'match_score',
    sort_order: 'desc'
  });
  const [filterOptions, setFilterOptions] = useState(null);

  useEffect(() => {
    loadFilterOptions();
    loadSuggestions();
  }, []);

  const loadFilterOptions = async () => {
    try {
      const response = await fetchWithAuth('http://localhost:5000/api/browse/filters');
      if (response.ok) {
        const data = await response.json();
        setFilterOptions(data);
      }
    } catch (err) {
      console.error('Failed to load filter options:', err);
    }
  };

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
      setSuggestions(data.suggestions || []);
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
      const response = await fetchWithAuth(`http://localhost:5000/api/interactions/like/${username}`, {
        method: 'POST'
      });
      if (response.ok) {
        const data = await response.json();
        if (data.match) {
          alert(`🎉 It's a match with ${username}!`);
        } else {
          alert(`💖 You liked ${username}`);
        }
      }
    } catch (err) {
      console.error('Error liking user:', err);
    }
  };

  if (loading && suggestions.length === 0) {
    return <div className="browse-loading">Loading suggestions...</div>;
  }

  return (
    <div className="browse-page">
      <div className="browse-header">
        <h1>Discover People</h1>
        <p>Find your perfect match based on your preferences and location</p>
      </div>

      {/* Filters Section */}
      <div className="filters-section">
        <h3>Filters & Sorting</h3>
        <div className="filters-grid">
          <div className="filter-group">
            <label>Age Range:</label>
            <div className="age-inputs">
              <input
                type="number"
                placeholder="Min"
                value={filters.min_age}
                onChange={(e) => handleFilterChange('min_age', e.target.value)}
                min={filterOptions?.age_range?.min || 18}
                max={filterOptions?.age_range?.max || 100}
              />
              <span>-</span>
              <input
                type="number"
                placeholder="Max"
                value={filters.max_age}
                onChange={(e) => handleFilterChange('max_age', e.target.value)}
                min={filterOptions?.age_range?.min || 18}
                max={filterOptions?.age_range?.max || 100}
              />
            </div>
          </div>

          <div className="filter-group">
            <label>Max Distance: {filters.max_distance}km</label>
            <input
              type="range"
              min="1"
              max="500"
              value={filters.max_distance}
              onChange={(e) => handleFilterChange('max_distance', e.target.value)}
              className="distance-slider"
            />
          </div>

          <div className="filter-group">
            <label>Fame Rating:</label>
            <div className="fame-inputs">
              <input
                type="number"
                placeholder="Min"
                value={filters.min_fame}
                onChange={(e) => handleFilterChange('min_fame', e.target.value)}
                min={0}
                max={100}
              />
              <span>-</span>
              <input
                type="number"
                placeholder="Max"
                value={filters.max_fame}
                onChange={(e) => handleFilterChange('max_fame', e.target.value)}
                min={0}
                max={100}
              />
            </div>
          </div>

          <div className="filter-group">
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

          <button className="apply-filters-btn" onClick={applyFilters}>
            Apply Filters
          </button>
        </div>
      </div>

      {/* Results Section */}
      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      <div className="suggestions-section">
        <h3>Suggestions ({suggestions.length})</h3>
        {loading && <div className="loading-overlay">Updating...</div>}
        
        {suggestions.length === 0 && !loading ? (
          <div className="no-results">
            <h4>No matches found</h4>
            <p>Try adjusting your filters to see more people</p>
          </div>
        ) : (
          <div className="suggestions-grid">
            {suggestions.map((person) => (
              <div key={person.username} className="suggestion-card">
                <div className="card-image">
                  {person.profile_picture ? (
                    <img 
                      src={person.profile_picture} 
                      alt={`${person.first_name}'s profile`}
                      onError={(e) => {
                        e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxjaXJjbGUgY3g9IjEwMCIgY3k9Ijc1IiByPSIzNSIgZmlsbD0iI0Q1RDlERiIvPgo8cGF0aCBkPSJNNTAgMTUwQzUwIDEyNS45IDY5IDEwNSA5NSAxMDVIMTA1QzEzMSAxMDUgMTUwIDEyNS45IDE1MCAxNTBWMTUwSDUwVjE1MFoiIGZpbGw9IiNENUQ5REYiLz4KPC9zdmc+';
                      }}
                    />
                  ) : (
                    <div className="placeholder-avatar">
                      <span>👤</span>
                    </div>
                  )}
                  <div className="match-score">
                    Match: {person.match_score}%
                  </div>
                </div>

                <div className="card-content">
                  <h4>{person.first_name} {person.last_name}</h4>
                  <div className="basic-info">
                    <span>📍 {person.distance ? `${person.distance}km away` : person.city}</span>
                    <span>🎂 {person.age} years old</span>
                    <span>⭐ {person.fame_rating}/100</span>
                  </div>

                  {person.bio && (
                    <p className="bio-preview">
                      {person.bio.length > 100 ? 
                        `${person.bio.substring(0, 100)}...` : 
                        person.bio
                      }
                    </p>
                  )}

                  {person.interests && person.interests.length > 0 && (
                    <div className="interests-preview">
                      {person.interests.slice(0, 3).map((interest, idx) => (
                        <span key={idx} className="interest-tag">{interest}</span>
                      ))}
                      {person.interests.length > 3 && (
                        <span className="more-interests">+{person.interests.length - 3} more</span>
                      )}
                    </div>
                  )}

                  {person.common_interests > 0 && (
                    <div className="common-interests">
                      🤝 {person.common_interests} shared interests
                    </div>
                  )}

                  {person.compatibility_reasons && person.compatibility_reasons.length > 0 && (
                    <div className="compatibility-reasons">
                      {person.compatibility_reasons.map((reason, idx) => (
                        <span key={idx} className="reason-tag">✓ {reason}</span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="card-actions">
                  <button 
                    className="like-btn"
                    onClick={() => handleLike(person.username)}
                  >
                    💖 Like
                  </button>
                  <button 
                    className="view-profile-btn"
                    onClick={() => window.open(`/profile/${person.username}`, '_blank')}
                  >
                    👤 View Profile
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default BrowsePage;