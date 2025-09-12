// src/pages/DiscoverPage.js
import React, { useMemo, useState } from "react";
import "./DiscoverPage.css";

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

// Demo data now has lat/lng and followers
const users = [
  { id: 1, name: "Sophia",  age: 28, followers: 2100, lat: 37.7749, lng: -122.4194, tags: ["Hiking","Photography","Travel"], avatar: "https://i.pravatar.cc/160?img=1" },
  { id: 2, name: "Ethan",   age: 32, followers: 120,  lat: 34.0522, lng: -118.2437, tags: ["Music","Cooking","Reading"],    avatar: "https://i.pravatar.cc/160?img=2" },
  { id: 3, name: "Olivia",  age: 25, followers: 980,  lat: 40.7128, lng: -74.0060,  tags: ["Art","Yoga","Movies"],        avatar: "https://i.pravatar.cc/160?img=3" },
  { id: 4, name: "Noah",    age: 30, followers: 4300, lat: 41.8781, lng: -87.6298,  tags: ["Gaming","Tech","Sports"],     avatar: "https://i.pravatar.cc/160?img=4" },
  { id: 5, name: "Ava",     age: 27, followers: 560,  lat: 29.7604, lng: -95.3698,  tags: ["Fashion","Brunch","Shopping"],avatar: "https://i.pravatar.cc/160?img=5" },
  { id: 6, name: "Liam",    age: 31, followers: 70,   lat: 47.6062, lng: -122.3321, tags: ["Fitness","Outdoors","Volunteering"], avatar: "https://i.pravatar.cc/160?img=6" },
];

// Common tags
const ALL_TAGS = [
  "Hiking","Reading","Cooking","Travel","Music","Art","Sports",
  "Movies","Gaming","Volunteering",
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
  // Filters
  const [minAge, setMinAge] = useState(18);
  const [maxAge, setMaxAge] = useState(60);

  const [followersMin, setFollowersMin] = useState(0); // "fame rating"
  const [selectedTags, setSelectedTags] = useState([]);

  // Map state
  const [center, setCenter] = useState({ lat: 39.5, lng: -98.35 }); // USA center
  const [radiusKm, setRadiusKm] = useState(500); // search radius

  // Toggle tag chips
  const toggleTag = (t) =>
    setSelectedTags((cur) =>
      cur.includes(t) ? cur.filter((x) => x !== t) : [...cur, t]
    );

  // Derived: filter users
  const filtered = useMemo(() => {
    return users.filter((u) => {
      if (u.age < minAge || u.age > maxAge) return false;
      if (u.followers < followersMin) return false;

      // tags: require at least one selected tag (if any chosen)
      if (selectedTags.length && !u.tags.some((t) => selectedTags.includes(t)))
        return false;

      // location: within radius (if user clicked the map at least once)
      if (center && radiusKm) {
        const d = haversineKm(center, { lat: u.lat, lng: u.lng });
        if (d > radiusKm) return false;
      }
      return true;
    });
  }, [minAge, maxAge, followersMin, selectedTags, center, radiusKm]);

  return (
    <div className="discover-container">
      <div className="discover-content">
        <h1>Discover</h1>

        {/* FILTERS */}
        <div className="filter-panel">
          <div className="filter-row">
            <div className="filter-col">
              <label>Age</label>
              <div className="range-2">
                <input
                  type="number"
                  min="18"
                  max={maxAge}
                  value={minAge}
                  onChange={(e) => setMinAge(Number(e.target.value))}
                />
                <span>to</span>
                <input
                  type="number"
                  min={minAge}
                  max="99"
                  value={maxAge}
                  onChange={(e) => setMaxAge(Number(e.target.value))}
                />
              </div>
            </div>

            <div className="filter-col">
              <label>Fame Rating (followers)</label>
              <input
                type="number"
                min="0"
                step="50"
                value={followersMin}
                onChange={(e) => setFollowersMin(Number(e.target.value))}
                placeholder="Min followers"
              />
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
        <div className="users-grid">
          {filtered.map((user) => (
            <div className="user-card" key={user.id}>
              <div className="avatar-wrapper">
                <img src={user.avatar} alt={user.name} />
              </div>
              <div className="user-info">
                <h3>
                  {user.name}, {user.age}
                </h3>
                <p className="meta">
                  Followers: <strong>{user.followers}</strong>
                </p>
                <div className="tags-inline">
                  {user.tags.map((t) => (
                    <span key={t} className="mini-chip">{t}</span>
                  ))}
                </div>
              </div>
            </div>
          ))}
          {!filtered.length && (
            <div className="empty">No matches with current filters.</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DiscoverPage;
