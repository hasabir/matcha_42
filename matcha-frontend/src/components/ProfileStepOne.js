import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { fetchWithAuth, addTags } from "../utils/api";
import "./ProfileStepOne.css";

/**
 * ProfileStepOne collects initial profile information from users:
 * gender, sexual preferences, bio, age, location (not sent as a column),
 * interests and photos. It sends a multipart/form-data request to
 * /api/profile/create_profile (with profile_pic, bio, gender, sexual_preferences,
 * age) and uploads additional photos separately. Interests are sent via
 * /add_tags. We no longer submit any of location / lat / lng / accuracy fields
 * because the `profiles` table does not have those columns.
 */

const ProfileStepOne = () => {
  const navigate = useNavigate();

  // State for form fields
  const [bio, setBio] = useState("");
  const [gender, setGender] = useState("");
  const [sexualPreferences, setSexualPreferences] = useState("");
  const [age, setAge] = useState("");
  const [location, setLocation] = useState("");
  const [interests, setInterests] = useState([]);

  // Photos: each photo is { file, url, isPrimary }
  const [photos, setPhotos] = useState([]);
  const fileInputRef = useRef(null);

  // Geolocation state (retained locally but not sent)
  const [coords, setCoords] = useState({ lat: null, lng: null, acc: null });
  const [locating, setLocating] = useState(false);

  // Form status and saving state
  const [status, setStatus] = useState(null);
  const [saving, setSaving] = useState(false);

  // Options
  const interestOptions = [
    "Hiking", "Reading", "Cooking", "Travel", "Music",
    "Art", "Sports", "Movies", "Gaming", "Volunteering",
  ];
  const genderOptions = [
    { label: "Female", value: "Female" },
    { label: "Male", value: "Male" },
    { label: "Non-binary", value: "Non-binary" },
    { label: "Other", value: "Other" },
  ];
  const sexualPreferenceOptions = [
    { label: "Women", value: "Women" },
    { label: "Men", value: "Men" },
    { label: "Both", value: "Both" },
    { label: "All", value: "All" },
  ];

  // Add files and set primary photo automatically
  const onPickFiles = (e) => {
    const files = Array.from(e.target.files || []);
    const appended = files.map((f) => ({
      file: f,
      url: URL.createObjectURL(f),
      isPrimary: false,
    }));
    const next = [...photos, ...appended].slice(0, 5);
    if (!next.some((p) => p.isPrimary) && next.length > 0) next[0].isPrimary = true;
    setPhotos(next);
  };

  // Set the primary photo by index
  const setPrimary = (idx) => {
    setPhotos((list) => list.map((p, i) => ({ ...p, isPrimary: i === idx })));
  };

  // Remove a photo; if the primary is removed, promote the first remaining
  const removeAt = (idx) => {
    setPhotos((list) => {
      const updated = list.filter((_, i) => i !== idx);
      if (!updated.some((p) => p.isPrimary) && updated.length > 0) {
        updated[0].isPrimary = true;
      }
      return updated;
    });
  };

  // Get geolocation via browser; fallback to IP-based lookup (results not sent to backend)
  const locateByGPS = () => {
    if (!("geolocation" in navigator)) return locateByIP();
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setCoords({
          lat: Number(pos.coords.latitude.toFixed(6)),
          lng: Number(pos.coords.longitude.toFixed(6)),
          acc: Math.round(pos.coords.accuracy),
        });
        setLocating(false);
      },
      () => {
        setLocating(false);
        locateByIP();
      },
      { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 }
    );
  };

  // Fallback to IP-based geolocation (results not sent to backend)
  const locateByIP = async () => {
    try {
      const res = await fetchWithAuth("http://localhost:5000/api/geo/ip");
      const data = await res.json().catch(() => null);
      if (data?.lat && data?.lng) {
        setCoords({ lat: data.lat, lng: data.lng, acc: data.acc || 1000 });
        if (!location && (data.city || data.neighborhood)) {
          setLocation(
            `${data.city || ""}${
              data.neighborhood ? ", " + data.neighborhood : ""
            }`.trim()
          );
        }
      }
    } catch {
      // ignore
    }
  };

  // Auto-locate on mount
  useEffect(() => {
    locateByGPS();
  }, []);

  // Toggle an interest
  const toggleInterest = (item) => {
    setInterests((prev) =>
      prev.includes(item) ? prev.filter((i) => i !== item) : [...prev, item]
    );
  };

  // Submit handler
  const handleNext = async (e) => {
    e.preventDefault();
    setStatus(null);

    // Simple validation
    if (!bio.trim()) return setStatus("Please write a short bio.");
    if (!gender) return setStatus("Please select your gender.");
    if (!sexualPreferences) return setStatus("Please select who you are interested in.");
    if (!age || isNaN(Number(age))) return setStatus("Please enter a valid age.");
    if (!location.trim()) return setStatus("Please enter your location.");

    setSaving(true);
    try {
      // Split primary and additional photos
      const primaryFile = photos.find((p) => p.isPrimary)?.file || null;
      const otherFiles = photos.filter((p) => !p.isPrimary).map((p) => p.file);

      // Construct multipart form data; send only known columns
      const formData = new FormData();
      if (primaryFile) formData.append("profile_pic", primaryFile);
      formData.append("bio", bio);
      formData.append("gender", gender);
      formData.append("sexual_preferences", sexualPreferences);
      formData.append("age", Number(age));

      // Get token from localStorage
      const token = localStorage.getItem("access_token");

      // 1) POST to create_profile
      const createRes = await fetch("http://localhost:5000/api/profile/create_profile", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });
      const createData = await createRes.json().catch(() => ({}));
      if (!createRes.ok) {
        if (Array.isArray(createData?.details) && createData.details.length) {
          setStatus(`Fix these fields: ${createData.details.join(", ")}`);
        } else {
          setStatus(
            createData.error || createData.message || "Could not save profile."
          );
        }
        setSaving(false);
        return;
      }

      // 2) Upload remaining photos
      if (otherFiles.length) {
        const uploadForm = new FormData();
        otherFiles.forEach((file) => uploadForm.append("images", file));
        try {
          await fetch("http://localhost:5000/api/profile/upload_images", {
            method: "POST",
            headers: {
              Authorization: `Bearer ${token}`,
            },
            body: uploadForm,
          });
        } catch (ex) {
          console.warn("upload_images failed", ex);
        }
      }

      // 3) Send interests as tags
      if (interests.length) {
        const tagsRes = await addTags(interests);
        if (!tagsRes.ok) {
          const body = await tagsRes.json().catch(() => ({}));
          console.warn("add_tags failed:", body);
        }
      }

      // 4) Go to the next step
      navigate("/dashboard");
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
        <div className="progress">
          <span>1 of 5</span>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: "20%" }}></div>
          </div>
        </div>

        <h2>What's your gender?</h2>
        <div className="button-group">
          {genderOptions.map((opt) => (
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

        <h2>Who are you interested in?</h2>
        <div className="button-group">
          {sexualPreferenceOptions.map((opt) => (
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
          onChange={(e) => setBio(e.target.value)}
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
              onChange={(e) => setAge(e.target.value)}
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
                onChange={(e) => setLocation(e.target.value)}
                placeholder="City, Country"
              />
              <button
                type="button"
                className="gps-btn"
                onClick={locateByGPS}
                disabled={locating}
              >
                {locating ? "Locating…" : "Use my GPS"}
              </button>
            </div>
            {coords.lat && coords.lng && (
              <small className="coords-hint">
                Detected: {coords.lat}, {coords.lng} (±{coords.acc}m)
              </small>
            )}
          </div>
        </div>

        <h2>What are your interests?</h2>
        <div className="chips-group">
          {interestOptions.map((opt) => (
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

        {/* Photo upload */}
        <h2>Add photos</h2>
        <p className="photo-hint">Add up to 5 photos, including a profile picture</p>
        <div className="photo-upload">
          <input
            ref={fileInputRef}
            id="fileInput"
            type="file"
            accept="image/*"
            multiple
            onChange={onPickFiles}
            style={{ display: "none" }}
          />
        </div>
        <label htmlFor="fileInput" className="upload-box">
          <p>Upload Photos</p>
          <span>Drag and drop or browse to upload</span>
        </label>

        <div className="thumbs">
          {photos.map((p, i) => (
            <div key={i} className={`thumb ${p.isPrimary ? "primary" : ""}`}>
              <img alt="thumbnail" src={p.url} />
              <div className="thumb-actions">
                <button type="button" onClick={() => setPrimary(i)}>
                  {p.isPrimary ? "Profile Photo" : "Set as Profile"}
                </button>
                <button type="button" onClick={() => removeAt(i)}>Remove</button>
              </div>
            </div>
          ))}
        </div>

        <button className="next-btn" onClick={handleNext} disabled={saving}>
          {saving ? "Saving…" : "Next"}
        </button>

        {status && <p className="status">{status}</p>}
      </div>
    </div>
  );
};

export default ProfileStepOne;
