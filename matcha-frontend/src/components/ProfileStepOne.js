import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./ProfileStepOne.css";

const ProfileStepOne = () => {
  const navigate = useNavigate();

  // Fields shown in UI (location is not sent to /create_profile; coords go to /set_location)
  const [bio, setBio] = useState("");
  const [gender, setGender] = useState("");
  const [sexualPreferences, setSexualPreferences] = useState("");
  const [age, setAge] = useState("");
  const [location, setLocation] = useState("");
  const [interests, setInterests] = useState([]);

  // Photos
  const [photos, setPhotos] = useState([]);
  const fileInputRef = useRef(null);

  // Geolocation
  const [coords, setCoords] = useState({ lat: null, lng: null, acc: null });
  const [locating, setLocating] = useState(false);

  const [status, setStatus] = useState(null);
  const [saving, setSaving] = useState(false);

  // Options for form
  const interestOptions = [
    "Hiking","Reading","Cooking","Travel","Music","Art",
    "Sports","Movies","Gaming","Volunteering"
  ];
  const genderOptions = [
    { label: "Female", value: "female" },
    { label: "Male", value: "male" },
    { label: "Other / Non-binary", value: "other" }
  ];
  const sexualPreferenceOptions = [
    { label: "Women", value: "female" },
    { label: "Men", value: "male" },
    { label: "Everyone", value: "both" }
  ];

  const onPickFiles = (e) => {
    const files = Array.from(e.target.files || []);
    // Validate file types
    const validFiles = files.filter(file => {
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
      if (!validTypes.includes(file.type)) {
      setStatus(`Invalid file type: ${file.name}. Please use JPG, PNG, GIF, or WebP.`);
        return false;
      }
      return true;
    });
    if (validFiles.length === 0) return;

    const appended = validFiles.map(f => ({ 
      file: f,
      url: URL.createObjectURL(f),
      isPrimary: false
    }));
    const next = [...photos, ...appended].slice(0, 5);
    if (!next.some(p => p.isPrimary) && next.length > 0) {
      next[0].isPrimary = true;
    }
    setPhotos(next);
    setStatus(null); // Clear any previous errors
  };

  const setPrimary = (idx) => {
    setPhotos(list => list.map((p, i) => ({ ...p, isPrimary: i === idx })));
  };

  const removeAt = (idx) => {
    setPhotos(list => {
      // Revoke the URL to prevent memory leaks
      const photoToRemove = list[idx];
      if (photoToRemove?.url) {
        URL.revokeObjectURL(photoToRemove.url);
      }
      const updated = list.filter((_, i) => i !== idx);
      if (!updated.some(p => p.isPrimary) && updated.length > 0) {
        updated[0].isPrimary = true;
      }
      return updated;
    });
  };

  const locateByGPS = async () => {
    if (!("geolocation" in navigator)) {
      alert("❌ Geolocation is not supported by your browser");
      return;
    }

    // Check permission status first
    try {
      if (navigator.permissions) {
        const permission = await navigator.permissions.query({ name: 'geolocation' });
        
        if (permission.state === 'denied') {
          alert(
            "📍 Location Access Blocked\n\n" +
            "You have blocked location access for this site.\n\n" +
            "To enable it:\n" +
            "1. Click the lock icon (🔒) in your browser's address bar\n" +
            "2. Find 'Location' in the permissions\n" +
            "3. Change it to 'Allow'\n" +
            "4. Refresh the page and try again\n\n" +
            "Or you can manually enter your city and country below."
          );
          return;
        }
      }
    } catch (e) {
      // Permission API not supported, continue anyway
      console.log("Permission API not available");
    }

    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      pos => {
        setCoords({
          lat: +pos.coords.latitude.toFixed(6),
          lng: +pos.coords.longitude.toFixed(6),
          acc: Math.round(pos.coords.accuracy)
        });
        setLocating(false);
      },
      async (error) => {
        setLocating(false);
        
        // Try IP-based fallback automatically
        try {
          const token = localStorage.getItem("access_token");
          const fallbackRes = await fetch("http://localhost:5000/api/profile/detect_location", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({})
          });
          
          if (fallbackRes.ok) {
            const fallbackData = await fallbackRes.json();
            if (fallbackData.location) {
              setLocation(fallbackData.location);
              if (fallbackData.latitude && fallbackData.longitude) {
                setCoords({
                  lat: fallbackData.latitude,
                  lng: fallbackData.longitude,
                  acc: fallbackData.accuracy || 5000
                });
              }
              alert("📍 Location detected from your IP address: " + fallbackData.location + "\n\nYou can update this manually if needed.");
              return;
            }
          }
        } catch (ipError) {
          console.error("IP fallback failed:", ipError);
        }
        
        // If IP fallback also fails, show appropriate message
        let message = "Failed to get your location. ";
        
        switch (error.code) {
          case error.PERMISSION_DENIED:
            message = 
              "📍 Location Access Denied\n\n" +
              "We tried to detect your location from your IP address but it didn't work.\n\n" +
              "To use GPS location:\n" +
              "1. Click the lock icon (🔒) in your browser's address bar\n" +
              "2. Change Location permission to 'Allow'\n" +
              "3. Refresh the page and try again\n\n" +
              "Or enter your location manually below.";
            break;
          case error.POSITION_UNAVAILABLE:
            message = "❌ Location information is unavailable. Please enter your location manually.";
            break;
          case error.TIMEOUT:
            message = "⏱️ Location request timed out. Please try again or enter your location manually.";
            break;
          default:
            message = "❌ An unknown error occurred. Please enter your location manually.";
        }
        
        alert(message);
      },
      { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 }
    );
  };

  useEffect(() => {
    locateByGPS();
    // Cleanup object URLs on unmount
    return () => {
      photos.forEach(photo => {
        if (photo?.url) {
          URL.revokeObjectURL(photo.url);
        }
      });
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const toggleInterest = (item) => {
    setInterests(prev => (
      prev.includes(item)
        ? prev.filter(i => i !== item)
        : [...prev, item]
    ));
  };

  const handleNext = async (e) => {
    e.preventDefault();
    setStatus(null);
    // Client validation
    if (!bio.trim()) return setStatus("Please write a short bio.");
    if (!gender) return setStatus("Please select your gender.");
    // Sexual preferences is now optional - if not specified, defaults to bisexual
    // if (!sexualPreferences) return setStatus("Please select your preference.");
    if (!age || isNaN(Number(age))) return setStatus("Please enter a valid age.");
    if (!location.trim()) return setStatus("Please enter your location.");

    setSaving(true);
    try {
      const token = localStorage.getItem("access_token");
      // Step 1: create profile
      const formData = new FormData();
      const primaryFile = photos.find(p => p.isPrimary)?.file;
      if (primaryFile) formData.append("profile_pic", primaryFile);
      formData.append("bio", bio);
      formData.append("gender", gender);
      // Only send sexual_preferences if it's specified (optional field, defaults to bisexual if not set)
      if (sexualPreferences) {
        formData.append("sexual_preferences", sexualPreferences);
      }
      formData.append("age", Number(age));

      const createRes = await fetch("http://localhost:5000/api/profile/create_profile", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData
      });
      const createData = await createRes.json().catch(() => ({}));
      if (!createRes.ok) {
        if (Array.isArray(createData.details) && createData.details.length) {
          setStatus(`Fix these fields: ${createData.details.join(", ")}`);
        } else {
          setStatus(createData.error || "Could not save profile.");
        }
        setSaving(false);
        return;
      }

      // Step 2: upload extra images
      const others = photos.filter(p => !p.isPrimary).map(p => p.file);
      if (others.length) {
        const uploadForm = new FormData();
        others.forEach(f => uploadForm.append("images", f));
        const uploadRes = await fetch("http://localhost:5000/api/profile/upload_images", {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: uploadForm
        });
        const uploadData = await uploadRes.json().catch(() => ({}));
        if (!uploadRes.ok) {
          console.error("Failed to upload additional images:", uploadData);
          setStatus(`Warning: ${uploadData.error || "Some images failed to upload"}. Please check your profile and try uploading them again from Account Settings.`);
          setSaving(false);
          // Continue to profile page after showing warning for 3 seconds
          setTimeout(() => navigate("/profile"), 3000);
          return;
        }
      }

      // Step 3: add tags
      if (interests.length) {
        await fetch("http://localhost:5000/api/profile/add_tags", {
          method: "POST",
          headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
          body: JSON.stringify({ tags: interests })
        });
      }

      // Step 4: set location with GPS coords and/or city/country text
      if (coords.lat && coords.lng || location.trim()) {
        // Parse location text to extract city and country
        let city = '';
        let country = '';
        if (location.trim()) {
          const parts = location.split(',').map(p => p.trim());
          if (parts.length >= 2) {
            city = parts[0];
            country = parts[1];
          } else if (parts.length === 1) {
            city = parts[0];
          }
        }
        
        await fetch("http://localhost:5000/api/profile/set_location", {
          method: "POST",
          headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
          body: JSON.stringify({
            latitude: coords.lat || null,
            longitude: coords.lng || null,
            city: city || null,
            country: country || null,
            accuracy: coords.acc || null
          })
        });
      }

      // Redirect on success
      navigate("/profile");
    } catch (err) {
      console.error(err);
      setStatus("Network error. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="step-container">
      <div className="step-content">
        <h2>What's your gender?</h2>
        <div className="button-group">
          {genderOptions.map(opt => (
            <button
              key={opt.value}
              type="button"
              className={`choice-btn ${gender === opt.value ? "selected" : ""}`}
              onClick={() => setGender(opt.value)}
            >
              {opt.label}
            </button>
          ))}
        </div>

        <h2>Who are you interested in? <span style={{fontSize: '0.85rem', fontWeight: 'normal', color: '#888'}}>(optional - defaults to "Both" if not specified)</span></h2>
        <div className="button-group">
          {sexualPreferenceOptions.map(opt => (
            <button
              key={opt.value}
              type="button"
              className={`choice-btn ${sexualPreferences === opt.value ? "selected" : ""}`}
              onClick={() => setSexualPreferences(opt.value)}
            >
              {opt.label}
            </button>
          ))}
        </div>

        <h2>Write a bio</h2>
        <textarea
          rows="4"
          placeholder="Tell us about yourself…"
          className="bio"
          value={bio}
          onChange={e => setBio(e.target.value)}
        />

        <div className="inline-two">
          <div className="inline-field">
            <label htmlFor="age">Age</label>
            <input
              id="age"
              type="number"
              min="18"
              max="120"
              value={age}
              onChange={e => setAge(e.target.value)}
              placeholder="e.g., 25"
            />
          </div>
          <div className="inline-field">
            <label htmlFor="location">Location</label>
            <div className="location-row">
              <input
                id="location"
                type="text"
                value={location}
                onChange={e => setLocation(e.target.value)}
                placeholder="City, Country"
              />
              <button
                type="button"
                className="gps-btn"
                onClick={locateByGPS}
                disabled={locating}
                title="Click to detect your location automatically. You'll need to allow location access in your browser."
              >
                {locating ? "Locating…" : "Use my GPS"}
              </button>
            </div>
          </div>
        </div>

        <h2>What are your interests?</h2>
        <div className="chips-group">
          {interestOptions.map(opt => (
            <button
              key={opt}
              type="button"
              className={`chip ${interests.includes(opt) ? "selected" : ""}`}
              onClick={() => toggleInterest(opt)}
            >
              {opt}
            </button>
          ))}
        </div>

        <h2>Add photos</h2>
        <p className="photo-hint">
          Add up to 5 photos total: 1 profile photo + 4 additional (JPG, PNG, GIF, or WebP).
          {photos.length > 0 && ` (${photos.length}/5 photos added)`}
        </p>
        <input
          ref={fileInputRef}
          id="fileInput"
          type="file"
          accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
          multiple
          onChange={onPickFiles}
          style={{ display: "none" }}
        />
        <label htmlFor="fileInput" className="upload-box">
          <p>📸 Upload Photos</p>
          <span>Click to browse or drag and drop images here</span>
        </label>

        {photos.length > 0 && (
          <div className="thumbs">
            {photos.map((p, i) => (
              <div
                key={`photo-${i}-${p.file?.name}`}
                className={`thumb ${p.isPrimary ? "primary" : ""}`}
              >
                <img
                  alt={`Photo ${i + 1}`}
                  src={p.url}
                  onError={(e) => {
                    console.error("Image load error:", p.url);
                    e.target.src =
                      'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect fill="%23ddd" width="100" height="100"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23999"%3EError%3C/text%3E%3C/svg%3E';
                  }}
                />
                {p.isPrimary && <span className="primary-badge">Profile Photo</span>}
                <div className="thumb-actions">
                  <button type="button" onClick={() => setPrimary(i)}>
                    {p.isPrimary ? "✓ Profile Photo" : "Set as Profile"}
                  </button>
                  <button type="button" onClick={() => removeAt(i)}>
                    ✕ Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        <button className="next-btn" onClick={handleNext} disabled={saving}>
          {saving ? "Saving…" : "Next"}
        </button>

        {status && <p className="status">{status}</p>}
      </div>
    </div>
  );
};

export default ProfileStepOne;
