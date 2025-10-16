// src/pages/DiscoverPage.js
import React, { useState, useEffect } from "react";
import { fetchWithAuth } from "../utils/api";
import "./DiscoverPage.css";
import "leaflet/dist/leaflet.css";

// ⬇️ Map
import { MapContainer, TileLayer, Circle, Marker, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Fix default marker assets (optional, keeps console quiet in CRA/Vite)
const defaultIcon = new L.Icon({
  iconUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = defaultIcon;

// Common tags - now loaded from backend
let ALL_TAGS = [
  "Hiking","Reading","Cooking","Travel","Music","Art","Sports",
  "Movies","Gaming","Volunteering","Technology","Photography","Fitness","Health","Dancing"
];

function haversineKm(a, b) {
  const R = 6371;
  const dLat = ((b.lat - a.lat) * Math.PI) / 180;
  const dLng = ((b.lng - a.lng) * Math.PI) / 180;
  const la1 = (a.lat * Math.PI) / 180;
  const la2 = (b.lat * Math.PI) / 180;
  const sinDLat = Math.sin(dLat / 2);
  const sinDLng = Math.sin(dLng / 2);
  const c =
    2 *
    Math.asin(
      Math.sqrt(
        sinDLat * sinDLat +
          Math.cos(la1) * Math.cos(la2) * sinDLng * sinDLng
      )
    );
  return R * c;
}

function ClickToSet({ onPick }) {
  useMapEvents({
    click(e) {
      onPick({ lat: e.latlng.lat, lng: e.latlng.lng });
    },
  });
  return null;
}

const DiscoverPage = () => {
  // State for suggestions and filters
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filters
  const [minAge, setMinAge] = useState('');
  const [maxAge, setMaxAge] = useState('');
  const [followersMin, setFollowersMin] = useState(''); // "fame rating"
  const [followersMax, setFollowersMax] = useState('');
  const [selectedTags, setSelectedTags] = useState([]);
  const [sortBy, setSortBy] = useState('match_score');

  // Map state
  const [center, setCenter] = useState({ lat: 40.7128, lng: -74.0060 }); // NYC default
  const [radiusKm, setRadiusKm] = useState(100); // search radius
  
  // Filter options from backend
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
        if (data.available_interests) {
          ALL_TAGS = data.available_interests;
        }
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
      if (minAge) params.append('min_age', minAge);
      if (maxAge) params.append('max_age', maxAge);
      if (followersMin) params.append('min_fame', followersMin);
      if (followersMax) params.append('max_fame', followersMax);
      if (radiusKm) params.append('max_distance', radiusKm);
      if (selectedTags.length > 0) params.append('common_tags', selectedTags.join(','));
      if (sortBy) params.append('sort_by', sortBy);
      params.append('sort_order', 'desc');

      const response = await fetchWithAuth(`http://localhost:5000/api/browse/suggestions?${params}`);
      if (!response.ok) throw new Error('Failed to load suggestions');
      
      const data = await response.json();
      setSuggestions(data.suggestions || []);
      setError(null);
    } catch (err) {
      console.error('Error loading suggestions:', err);
      setError(err.message);
      // Fallback to empty array on error
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  };

  // Toggle tag chips
  const toggleTag = (t) => {
    setSelectedTags((cur) =>
      cur.includes(t) ? cur.filter((x) => x !== t) : [...cur, t]
    );
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

  const applyFilters = () => {
    loadSuggestions();
  };

  return (
    <div className="discover-container">
      <div className="discover-content">
        <h1>Discover</h1>

        {/* FILTERS */}
        <div className="filter-panel">
          <div className="filter-row">
            <div className="filter-col">
              <label>Age Range</label>
              <div className="range-2">
                <input
                  type="number"
                  min="18"
                  max="100"
                  value={minAge}
                  onChange={(e) => setMinAge(e.target.value)}
                  placeholder="Min"
                />
                <span>to</span>
                <input
                  type="number"
                  min="18"
                  max="100"
                  value={maxAge}
                  onChange={(e) => setMaxAge(e.target.value)}
                  placeholder="Max"
                />
              </div>
            </div>

            <div className="filter-col">
              <label>Fame Rating</label>
              <div className="range-2">
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={followersMin}
                  onChange={(e) => setFollowersMin(e.target.value)}
                  placeholder="Min"
                />
                <span>to</span>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={followersMax}
                  onChange={(e) => setFollowersMax(e.target.value)}
                  placeholder="Max"
                />
              </div>
            </div>
            
            <div className="filter-col">
              <label>Sort By</label>
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                <option value="match_score">Best Match</option>
                <option value="distance">Distance</option>
                <option value="age">Age</option>
                <option value="fame_rating">Fame Rating</option>
                <option value="common_tags">Common Interests</option>
              </select>
            </div>
          </div>

          <div className="filter-row">
            <div className="filter-col">
              <label>Common Tags</label>
              <div className="chips">
                {ALL_TAGS.map((t) => (
                  <button
                    key={t}
                    className={`chip ${selectedTags.includes(t) ? "selected" : ""}`}
                    onClick={() => toggleTag(t)}
                    type="button"
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>
          </div>
          
          <div className="filter-row">
            <div className="filter-col">
              <button className="apply-filters-btn" onClick={applyFilters}>
                🔍 Apply Filters ({suggestions.length} matches)
              </button>
            </div>
          </div>

          <div className="filter-row">
            <div className="filter-col">
              <label>Location (click map to set)</label>
              <div className="map-wrap">
                <MapContainer
                  center={[center.lat, center.lng]}
                  zoom={4}
                  className="leaflet-map"
                  scrollWheelZoom={true}
                >
                  <TileLayer
                    attribution='&copy; OpenStreetMap'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  <ClickToSet onPick={setCenter} />
                  <Marker position={[center.lat, center.lng]} />
                  <Circle
                    center={[center.lat, center.lng]}
                    radius={radiusKm * 1000}
                    pathOptions={{ color: "#2563eb" }}
                  />
                </MapContainer>
                <div className="radius-row">
                  <span>Radius:</span>
                  <input
                    type="range"
                    min="10"
                    max="2000"
                    step="10"
                    value={radiusKm}
                    onChange={(e) => setRadiusKm(Number(e.target.value))}
                  />
                  <strong>{radiusKm} km</strong>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* RESULTS */}
        {loading && (
          <div className="loading">
            <p>🔍 Finding your perfect matches...</p>
          </div>
        )}
        
        {error && (
          <div className="error-message">
            ❌ {error}
            <button onClick={loadSuggestions}>Try Again</button>
          </div>
        )}

        {!loading && !error && (
          <div className="users-grid">
            {suggestions.map((user) => (
              <div className="user-card" key={user.username}>
                <div className="avatar-wrapper">
                  {user.profile_picture ? (
                    <img 
                      src={user.profile_picture} 
                      alt={`${user.first_name}'s profile`}
                      onError={(e) => {
                        e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYwIiBoZWlnaHQ9IjE2MCIgdmlld0JveD0iMCAwIDE2MCAxNjAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxNjAiIGhlaWdodD0iMTYwIiBmaWxsPSIjRjNGNEY2Ii8+CjxjaXJjbGUgY3g9IjgwIiBjeT0iNjAiIHI9IjI4IiBmaWxsPSIjRDVEOURGIi8+CjxwYXRoIGQ9Ik00MCAyMEM0MCA5MC43IDU1LjIgNzYgNzYgNzZIODRDMTA0LjggNzYgMTIwIDkwLjcgMTIwIDEyMFYxMjBINDBWMTIwWiIgZmlsbD0iI0Q1RDlERiIvPgo8L3N2Zz4=';
                      }}
                    />
                  ) : (
                    <div className="placeholder-avatar">👤</div>
                  )}
                  {user.match_score && (
                    <div className="match-badge">
                      Match: {Math.round(user.match_score)}%
                    </div>
                  )}
                </div>
                <div className="user-info">
                  <h3>
                    {user.first_name} {user.last_name}, {user.age}
                  </h3>
                  <p className="meta">
                    📍 {user.distance ? `${user.distance}km away` : `${user.city}, ${user.country}`}
                  </p>
                  <p className="meta">
                    ⭐ Fame: <strong>{user.fame_rating}/100</strong>
                    {user.common_interests > 0 && (
                      <span> • 🤝 {user.common_interests} shared</span>
                    )}
                  </p>
                  
                  {user.bio && (
                    <p className="bio-preview">
                      {user.bio.length > 80 ? `${user.bio.substring(0, 80)}...` : user.bio}
                    </p>
                  )}
                  
                  <div className="tags-inline">
                    {(user.interests || []).slice(0, 4).map((t, idx) => (
                      <span 
                        key={idx} 
                        className={`mini-chip ${selectedTags.includes(t) ? 'highlighted' : ''}`}
                      >
                        {t}
                      </span>
                    ))}
                    {user.interests && user.interests.length > 4 && (
                      <span className="mini-chip more">+{user.interests.length - 4}</span>
                    )}
                  </div>

                  {user.compatibility_reasons && user.compatibility_reasons.length > 0 && (
                    <div className="compatibility-badges">
                      {user.compatibility_reasons.slice(0, 2).map((reason, idx) => (
                        <span key={idx} className="compatibility-badge">
                          ✓ {reason}
                        </span>
                      ))}
                    </div>
                  )}
                  
                  <div className="user-actions">
                    <button 
                      className="like-btn"
                      onClick={() => handleLike(user.username)}
                    >
                      💖 Like
                    </button>
                    <button 
                      className="view-profile-btn"
                      onClick={() => window.open(`/profile/${user.username}`, '_blank')}
                    >
                      👤 Profile
                    </button>
                  </div>
                </div>
              </div>
            ))}
            
            {!loading && suggestions.length === 0 && (
              <div className="empty">
                <h3>No matches found 😔</h3>
                <p>Try adjusting your filters to discover more people!</p>
                <button onClick={() => {
                  setMinAge('');
                  setMaxAge('');
                  setFollowersMin('');
                  setFollowersMax('');
                  setSelectedTags([]);
                  setRadiusKm(100);
                  setTimeout(loadSuggestions, 100);
                }}>
                  Reset Filters
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DiscoverPage;
