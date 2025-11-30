// src/pages/DiscoverPage.js
import React, { useState, useEffect } from "react";
import { fetchWithAuth } from "../utils/api";
import { API_BASE_URL } from "../config/api";
import "./DiscoverPage.css";
import "leaflet/dist/leaflet.css";

// ⬇️ Map
import { MapContainer, TileLayer, Circle, Marker, useMapEvents, GeoJSON } from "react-leaflet";
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

// Country coordinates for quick search
const COUNTRY_CENTERS = {
  'Morocco': { lat: 31.7917, lng: -7.0926, zoom: 6 },
  'France': { lat: 46.2276, lng: 2.2137, zoom: 6 },
  'Spain': { lat: 40.4637, lng: -3.7492, zoom: 6 },
  'Italy': { lat: 41.8719, lng: 12.5674, zoom: 6 },
  'Germany': { lat: 51.1657, lng: 10.4515, zoom: 6 },
  'United Kingdom': { lat: 55.3781, lng: -3.4360, zoom: 6 },
  'USA': { lat: 37.0902, lng: -95.7129, zoom: 4 },
  'Canada': { lat: 56.1304, lng: -106.3468, zoom: 4 },
};

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

function ClickToSet({ onPick, onCountryDetect }) {
  useMapEvents({
    async click(e) {
      onPick({ lat: e.latlng.lat, lng: e.latlng.lng });
      
      // Reverse geocode to get country name
      if (onCountryDetect) {
        try {
          const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${e.latlng.lat}&lon=${e.latlng.lng}&zoom=3`
          );
          const data = await response.json();
          if (data.address && data.address.country) {
            onCountryDetect(data.address.country);
          }
        } catch (error) {
          console.error('Error detecting country:', error);
        }
      }
    },
  });
  return null;
}

const DiscoverPage = () => {
  // Simplified state management - single search workflow
  const [displayedResults, setDisplayedResults] = useState([]); // Results displayed to user
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Filters - all applied in one advanced search
  const [minAge, setMinAge] = useState('');
  const [maxAge, setMaxAge] = useState('');
  const [followersMin, setFollowersMin] = useState(''); // "fame rating"
  const [followersMax, setFollowersMax] = useState('');
  const [selectedTags, setSelectedTags] = useState([]);
  const [sortBy, setSortBy] = useState('fame_rating');
  const [sortOrder, setSortOrder] = useState('desc');
  const [interestMatchMode, setInterestMatchMode] = useState('OR');
  const [genderFilter, setGenderFilter] = useState(''); // New: gender filter

  // Map state
  const [center, setCenter] = useState({ lat: 40.7128, lng: -74.0060 }); // NYC default
  const [radiusKm, setRadiusKm] = useState(500); // search radius - Increased default to 500km to catch more users
  const [useMapSearch, setUseMapSearch] = useState(false); // Toggle between map and text input - DEFAULT TO FALSE
  const [selectedCountryOnMap, setSelectedCountryOnMap] = useState(''); // Country selected on map
  
  // Text-based location filters
  const [cityFilter, setCityFilter] = useState('');
  const [countryFilter, setCountryFilter] = useState('');
  
  // Filter options from backend
  const [filterOptions, setFilterOptions] = useState(null);

  useEffect(() => {
    loadFilterOptions();
    performAdvancedSearch(); // Initial search on component mount
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

  // ADVANCED SEARCH - All filters and sorting in ONE request
  const performAdvancedSearch = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Build search criteria with ALL filters at once
      const searchCriteria = {};
      
      // Age range filter (SUBJECT REQUIREMENT)
      if (minAge || maxAge) {
        searchCriteria.age_range = {};
        if (minAge) searchCriteria.age_range.min_age = parseInt(minAge);
        if (maxAge) searchCriteria.age_range.max_age = parseInt(maxAge);
      }
      
      // Fame rating filter (SUBJECT REQUIREMENT)
      if (followersMin || followersMax) {
        searchCriteria.fame_rating = {};
        if (followersMin) searchCriteria.fame_rating.min = parseInt(followersMin);
        if (followersMax) searchCriteria.fame_rating.max = parseInt(followersMax);
      }
      
      // Location filter (SUBJECT REQUIREMENT)
      // Only add location filters if explicitly set by user
      if (useMapSearch && center && radiusKm) {
        // Only use GPS search if explicitly enabled
        searchCriteria.coordinates = {
          latitude: center.lat,
          longitude: center.lng,
          distance: radiusKm
        };
      } else if (!useMapSearch && (cityFilter || countryFilter)) {
        // Only use city/country filter if explicitly set
        searchCriteria.location = {};
        if (cityFilter) searchCriteria.location.city = cityFilter;
        if (countryFilter) searchCriteria.location.country = countryFilter;
      }
      // If no location filters are set, backend will return all users (no location filtering)
      
      // Interest tags filter (SUBJECT REQUIREMENT)
      if (selectedTags.length > 0) {
        searchCriteria.interests = selectedTags;
        searchCriteria.interests_match_mode = interestMatchMode;
      }
      
      // Gender filter (optional enhancement)
      if (genderFilter) {
        searchCriteria.gender = genderFilter;
      }
      
      // Sorting (SUBJECT REQUIREMENT)
      searchCriteria.sort_by = sortBy;
      searchCriteria.sort_order = sortOrder;
      
      console.log('🔍 Advanced Search with all criteria:', searchCriteria);

      // ONE API call with all criteria
      const response = await fetchWithAuth('http://localhost:5000/api/browse/search/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(searchCriteria)
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Failed to load search results');
      }
      
      const data = await response.json();
      let results = data.results || [];
      
      console.log(`✅ Advanced search returned ${results.length} results`);
      console.log('📸 First user profile_picture:', results[0]?.profile_picture);
      console.log('🖼️ Sample user data:', results[0]);
      
      // If GPS search returns no results, suggest trying city/country search
      if (results.length === 0 && searchCriteria.coordinates) {
        console.log('⚠️ GPS search returned 0 results. Users may not have GPS coordinates set.');
        setError('No users found with GPS coordinates in this area. Try using City/Country search instead, or expand your search radius.');
      } else {
        setError(null);
      }
      
      setDisplayedResults(results);
    } catch (err) {
      console.error('Error performing advanced search:', err);
      setError(err.message || 'Failed to search. Please check your filters and try again.');
      setDisplayedResults([]);
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

  // Handle country selection from map (quick country buttons)
  const selectCountryOnMap = (countryName) => {
    const countryData = COUNTRY_CENTERS[countryName];
    if (countryData) {
      setCenter({ lat: countryData.lat, lng: countryData.lng });
      setSelectedCountryOnMap(countryName);
      // Auto-switch to city/country search and set the country filter
      setUseMapSearch(false);
      setCountryFilter(countryName);
      // Trigger search with the new country filter
      setTimeout(() => performAdvancedSearch(), 100);
    }
  };

  // Handle country detection from map click
  const handleCountryDetected = (countryName) => {
    console.log('🗺️ Detected country from map click:', countryName);
    setSelectedCountryOnMap(countryName);
    // Auto-switch to city/country search and set the country filter
    setUseMapSearch(false);
    setCountryFilter(countryName);
    // Trigger search with the new country filter
    setTimeout(() => performAdvancedSearch(), 100);
  };

  const handleLike = async (username) => {
    try {
      console.log(`Liking user: ${username}`);
      const response = await fetchWithAuth(`http://localhost:5000/api/interactions/like/${username}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Like response:', data);
        
        if (data.match || data.result === "Match! You both like each other.") {
          // It's a match!
          alert(`🎉 It's a match with ${username}! You can now chat with each other.`);
        } else {
          // Just a like
          alert(`💖 You liked ${username}!`);
        }
        
        // Immediately remove the liked user from the displayed results
        setDisplayedResults(prevResults => prevResults.filter(user => user.username !== username));
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('Error liking user:', errorData);
        alert(`Failed to like ${username}: ${errorData.error || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Error liking user:', err);
      alert(`Error: ${err.message || 'Failed to like user'}`);
    }
  };

  // Reset all filters and perform new search
  const resetFilters = () => {
    setMinAge('');
    setMaxAge('');
    setFollowersMin('');
    setFollowersMax('');
    setSelectedTags([]);
    setRadiusKm(100);
    setCityFilter('');
    setCountryFilter('');
    setSelectedCountryOnMap('');
    setInterestMatchMode('OR');
    setSortOrder('desc');
    setSortBy('fame_rating');
    setGenderFilter('');
    
    // Trigger new search with reset filters
    setTimeout(() => performAdvancedSearch(), 100);
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
              <label>Gender</label>
              <select value={genderFilter} onChange={(e) => setGenderFilter(e.target.value)}>
                <option value="">All Genders</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
            
            <div className="filter-col">
              <label>Sort By</label>
              <select 
                value={sortBy} 
                onChange={(e) => setSortBy(e.target.value)}
                disabled={!useMapSearch && sortBy === 'distance'}
              >
                <option value="fame_rating">Fame Rating</option>
                <option value="distance" disabled={!useMapSearch}>
                  Distance {!useMapSearch && '(GPS only)'}
                </option>
                <option value="age">Age</option>
                <option value="interests">Common Interests</option>
                <option value="city">City</option>
                <option value="country">Country</option>
              </select>
            </div>

            <div className="filter-col">
              <label>Sort Order</label>
              <select value={sortOrder} onChange={(e) => setSortOrder(e.target.value)}>
                <option value="desc">Descending (High to Low)</option>
                <option value="asc">Ascending (Low to High)</option>
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
              <label>Interest Match Mode</label>
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                  <input
                    type="radio"
                    name="matchMode"
                    value="OR"
                    checked={interestMatchMode === 'OR'}
                    onChange={(e) => setInterestMatchMode(e.target.value)}
                    style={{ marginRight: '5px' }}
                  />
                  Match ANY tag (OR)
                </label>
                <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                  <input
                    type="radio"
                    name="matchMode"
                    value="AND"
                    checked={interestMatchMode === 'AND'}
                    onChange={(e) => setInterestMatchMode(e.target.value)}
                    style={{ marginRight: '5px' }}
                  />
                  Match ALL tags (AND)
                </label>
              </div>
            </div>
          </div>
          
          <div className="filter-row">
            <div className="filter-col">
              <label>Location Search Type</label>
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '10px' }}>
                <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                  <input
                    type="radio"
                    name="searchType"
                    checked={useMapSearch}
                    onChange={() => setUseMapSearch(true)}
                    style={{ marginRight: '5px' }}
                  />
                  Map-based (GPS)
                </label>
                <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                  <input
                    type="radio"
                    name="searchType"
                    checked={!useMapSearch}
                    onChange={() => setUseMapSearch(false)}
                    style={{ marginRight: '5px' }}
                  />
                  City/Country Name ⭐ <small>(Recommended)</small>
                </label>
              </div>
              
              {useMapSearch && (
                <div style={{ padding: '8px', backgroundColor: '#fff3cd', border: '1px solid #ffc107', borderRadius: '4px', marginBottom: '10px', fontSize: '0.85em' }}>
                  ⚠️ <strong>Note:</strong> GPS search only shows users with exact GPS coordinates. Many users only have city/country set. Consider using City/Country search for better results.
                </div>
              )}

              {!useMapSearch && (
                <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                  <div style={{ flex: 1 }}>
                    <input
                      type="text"
                      placeholder="City (e.g., Paris)"
                      value={cityFilter}
                      onChange={(e) => setCityFilter(e.target.value)}
                      style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
                      list="cities-list"
                    />
                    {filterOptions && filterOptions.available_cities && (
                      <datalist id="cities-list">
                        {filterOptions.available_cities.map(city => (
                          <option key={city} value={city} />
                        ))}
                      </datalist>
                    )}
                  </div>
                  <div style={{ flex: 1 }}>
                    <input
                      type="text"
                      placeholder="Country (e.g., France)"
                      value={countryFilter}
                      onChange={(e) => setCountryFilter(e.target.value)}
                      style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
                      list="countries-list"
                    />
                    {filterOptions && filterOptions.available_countries && (
                      <datalist id="countries-list">
                        {filterOptions.available_countries.map(country => (
                          <option key={country} value={country} />
                        ))}
                      </datalist>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Quick Country Selection */}
          <div className="filter-row">
            <div className="filter-col">
              <label>🗺️ Quick Country Search</label>
              <div style={{ 
                display: 'flex', 
                flexWrap: 'wrap', 
                gap: '8px', 
                padding: '10px', 
                backgroundColor: '#f8f9fa', 
                borderRadius: '8px',
                border: '1px solid #dee2e6'
              }}>
                {Object.keys(COUNTRY_CENTERS).map((country) => (
                  <button
                    key={country}
                    onClick={() => selectCountryOnMap(country)}
                    className={`country-select-btn ${selectedCountryOnMap === country ? 'active' : ''}`}
                    style={{
                      padding: '8px 16px',
                      borderRadius: '20px',
                      border: selectedCountryOnMap === country ? '2px solid #2563eb' : '1px solid #ccc',
                      backgroundColor: selectedCountryOnMap === country ? '#2563eb' : 'white',
                      color: selectedCountryOnMap === country ? 'white' : '#333',
                      cursor: 'pointer',
                      fontWeight: selectedCountryOnMap === country ? 'bold' : 'normal',
                      transition: 'all 0.2s ease',
                      fontSize: '0.9em'
                    }}
                    title={`Find users in ${country}`}
                  >
                    {country === 'Morocco' ? '🇲🇦' : 
                     country === 'France' ? '🇫🇷' : 
                     country === 'Spain' ? '🇪🇸' : 
                     country === 'Italy' ? '🇮🇹' : 
                     country === 'Germany' ? '🇩🇪' : 
                     country === 'United Kingdom' ? '🇬🇧' : 
                     country === 'USA' ? '🇺🇸' : 
                     country === 'Canada' ? '🇨🇦' : '🌍'} {country}
                  </button>
                ))}
              </div>
              <div style={{ 
                marginTop: '8px', 
                fontSize: '0.85em', 
                color: '#6c757d',
                fontStyle: 'italic',
                padding: '8px',
                backgroundColor: '#e7f3ff',
                borderRadius: '4px'
              }}>
                💡 Click a country above to instantly search for users in that country
              </div>
            </div>
          </div>

          {/* Always show map for country selection */}
          <div className="filter-row">
            <div className="filter-col">
              <label>🗺️ Interactive Map - Click anywhere to search users in that country</label>
              <div style={{ 
                padding: '8px', 
                backgroundColor: '#d4edda', 
                border: '1px solid #28a745', 
                borderRadius: '4px', 
                marginBottom: '10px', 
                fontSize: '0.9em',
                color: '#155724'
              }}>
                🎯 <strong>How to use:</strong> Click anywhere on the map (e.g., click on Morocco) and it will automatically detect the country and search for users there!
                {selectedCountryOnMap && (
                  <div style={{ marginTop: '5px', fontWeight: 'bold', color: '#0c5620' }}>
                    ✅ Currently searching in: {selectedCountryOnMap}
                  </div>
                )}
              </div>
              <div className="map-wrap">
                <MapContainer
                  center={[center.lat, center.lng]}
                  zoom={2}
                  className="leaflet-map"
                  scrollWheelZoom={true}
                >
                  <TileLayer
                    attribution='&copy; OpenStreetMap'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  <ClickToSet onPick={setCenter} onCountryDetect={handleCountryDetected} />
                  <Marker position={[center.lat, center.lng]} />
                  {useMapSearch && (
                    <Circle
                      center={[center.lat, center.lng]}
                      radius={radiusKm * 1000}
                      pathOptions={{ color: "#2563eb" }}
                    />
                  )}
                </MapContainer>
                {useMapSearch && (
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
                )}
              </div>
            </div>
          </div>

          <div className="filter-row">
            <div className="filter-col" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ fontSize: '0.9em', color: '#666', fontStyle: 'italic', padding: '10px', backgroundColor: '#f0f8ff', borderRadius: '4px', border: '1px solid #d0e8ff' }}>
                📋 <strong>Advanced Search:</strong> Set your filters (age, fame, location, interests, gender) and click Search.
                <br />
                <span style={{ fontSize: '0.85em' }}>
                  All filters and sorting are applied in one search. Leave filters empty to see all users.
                </span>
                <br />
                <span style={{ fontSize: '0.85em', color: '#e67e22' }}>
                  💡 <strong>Location Tip:</strong> GPS search only finds users with exact coordinates. Use <strong>City/Country search</strong> for better results!
                </span>
              </div>
              <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
                <button 
                  className="apply-filters-btn" 
                  onClick={performAdvancedSearch}
                  style={{ backgroundColor: '#2563eb', fontWeight: 'bold', fontSize: '1.1em', padding: '12px 24px' }}
                  title="Search with all selected filters and sorting"
                >
                  🔍 Search
                </button>

                <button 
                  className="apply-filters-btn" 
                  onClick={resetFilters}
                  style={{ backgroundColor: '#6c757d' }}
                  title="Reset all filters and search again"
                >
                  🔄 Reset Filters
                </button>
                <div style={{ marginLeft: 'auto', color: '#666', display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <span>
                    Found <strong>{displayedResults.length}</strong> result{displayedResults.length !== 1 ? 's' : ''}
                  </span>
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
          <div className="error-message" style={{ backgroundColor: '#fff3cd', border: '2px solid #ffc107', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
            <div style={{ marginBottom: '10px' }}>
              ❌ {error}
            </div>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              {useMapSearch && (
                <button 
                  onClick={() => {
                    setUseMapSearch(false);
                    setError(null);
                  }}
                  style={{ backgroundColor: '#28a745', color: 'white', padding: '8px 16px', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
                >
                  Switch to City/Country Search
                </button>
              )}
              <button 
                onClick={performAdvancedSearch}
                style={{ backgroundColor: '#007bff', color: 'white', padding: '8px 16px', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
              >
                Try Again
              </button>
            </div>
          </div>
        )}

        {!loading && !error && (
          <div className="users-grid">
            {displayedResults.map((user, index) => (
              <div 
                className="user-card" 
                key={user.username}
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="avatar-wrapper">
                  {user.profile_picture ? (
                    <img 
                      src={`${API_BASE_URL}${user.profile_picture}`}
                      alt={`${user.first_name}'s profile`}
                      onError={(e) => {
                        console.error('Error loading image:', `${API_BASE_URL}${user.profile_picture}`);
                        e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYwIiBoZWlnaHQ9IjE2MCIgdmlld0JveD0iMCAwIDE2MCAxNjAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxNjAiIGhlaWdodD0iMTYwIiBmaWxsPSIjRjNGNEY2Ii8+CjxjaXJjbGUgY3g9IjgwIiBjeT0iNjAiIHI9IjI4IiBmaWxsPSIjRDVEOURGIi8+CjxwYXRoIGQ9Ik00MCAyMEM0MCA5MC43IDU1LjIgNzYgNzYgNzZIODRDMTA0LjggNzYgMTIwIDkwLjcgMTIwIDEyMFYxMjBINDBWMTIwWiIgZmlsbD0iI0Q1RDlERiIvPgo8L3N2Zz4=';
                      }}
                    />
                  ) : (
                    <div className="placeholder-avatar">
                      <svg width="100%" height="100%" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect width="200" height="200" fill="url(#grad1)"/>
                        <defs>
                          <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style={{stopColor: '#fce7f3', stopOpacity: 1}} />
                            <stop offset="100%" style={{stopColor: '#e7f0fc', stopOpacity: 1}} />
                          </linearGradient>
                        </defs>
                        <circle cx="100" cy="80" r="35" fill="#D5D9DF"/>
                        <path d="M50 200C50 155 70 130 100 130C130 130 150 155 150 200" fill="#D5D9DF"/>
                        <text x="100" y="215" fontSize="16" fill="#6b7280" textAnchor="middle" fontWeight="600">No Photo</text>
                      </svg>
                    </div>
                  )}
                  {user.match_score && (
                    <div className="match-badge">
                      <span className="match-icon">🎯</span>
                      <span className="match-text">{Math.round(user.match_score)}%</span>
                    </div>
                  )}
                  <div className="online-indicator" title="Recently active">
                    <span className="pulse-ring"></span>
                  </div>
                  <div className="avatar-overlay"></div>
                </div>
                <div className="user-info">
                  <div className="user-header">
                    <div className="user-name-wrapper">
                      <h3>
                        {user.first_name} {user.last_name}
                      </h3>
                      {user.fame_rating && (
                        <div className="fame-badge">
                          <span className="fame-icon">⭐</span>
                          <span className="fame-value">{user.fame_rating}</span>
                        </div>
                      )}
                    </div>
                    <span className="user-age">{user.age}</span>
                  </div>
                  
                  <div className="user-stats">
                    <div className="stat-item location-stat">
                      <div className="stat-icon-wrapper">
                        <span className="stat-icon">📍</span>
                      </div>
                      <span className="stat-text">
                        {user.distance ? `${user.distance}km away` : (user.city || user.country || 'Location not set')}
                      </span>
                    </div>
                    {user.common_interests > 0 && (
                      <div className="stat-item interests-stat">
                        <div className="stat-icon-wrapper">
                          <span className="stat-icon">🤝</span>
                        </div>
                        <span className="stat-text">
                          <strong>{user.common_interests}</strong> shared interest{user.common_interests !== 1 ? 's' : ''}
                        </span>
                      </div>
                    )}
                  </div>
                  
                  {user.bio && (
                    <div className="bio-container">
                      <p className="bio-preview">
                        {user.bio.length > 100 ? `${user.bio.substring(0, 100)}...` : user.bio}
                      </p>
                    </div>
                  )}
                  
                  {(user.interests && user.interests.length > 0) && (
                    <div className="tags-inline">
                      {user.interests.slice(0, 4).map((t, idx) => (
                        <span 
                          key={idx} 
                          className={`mini-chip ${selectedTags.includes(t) ? 'highlighted' : ''}`}
                        >
                          {selectedTags.includes(t) && <span className="sparkle">✨</span>}
                          <span className="chip-text">{t}</span>
                        </span>
                      ))}
                      {user.interests.length > 4 && (
                        <span className="mini-chip more">
                          +{user.interests.length - 4} more
                        </span>
                      )}
                    </div>
                  )}

                  {user.compatibility_reasons && user.compatibility_reasons.length > 0 && (
                    <div className="compatibility-badges">
                      {user.compatibility_reasons.slice(0, 2).map((reason, idx) => (
                        <span key={idx} className="compatibility-badge">
                          <span className="check-icon">✓</span>
                          <span>{reason}</span>
                        </span>
                      ))}
                    </div>
                  )}
                  
                  <div className="user-actions">
                    <button 
                      className="like-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleLike(user.username);
                      }}
                      title="Like this profile"
                    >
                      <span className="btn-icon">💖</span>
                      <span className="btn-text">Like</span>
                    </button>
                    <button 
                      className="view-profile-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        window.open(`/profile/${user.username}`, '_blank');
                      }}
                      title="View full profile"
                    >
                      <span className="btn-icon">👤</span>
                      <span className="btn-text">View Profile</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
            
            {!loading && displayedResults.length === 0 && !error && (
              <div className="empty">
                <h3>No matches found 😔</h3>
                <p>
                  Try adjusting your filters (age, fame, location, interests, gender) or expanding your search radius.
                </p>
                {useMapSearch && (
                  <p style={{ color: '#e67e22', fontWeight: 'bold', marginTop: '10px' }}>
                    💡 <strong>Tip:</strong> GPS search only finds users with exact coordinates. Try switching to <strong>City/Country search</strong>!
                  </p>
                )}
                <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', flexWrap: 'wrap', marginTop: '15px' }}>
                  {useMapSearch && (
                    <button 
                      onClick={() => {
                        setUseMapSearch(false);
                        performAdvancedSearch();
                      }}
                      style={{ backgroundColor: '#28a745', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
                    >
                      Switch to City/Country Search
                    </button>
                  )}
                  <button onClick={resetFilters}>
                    Reset Filters
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DiscoverPage;
