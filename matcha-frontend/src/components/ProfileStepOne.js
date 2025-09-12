// src/components/ProfileStepOne.js
import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { fetchWithAuth, addTags } from "../utils/api";   // ← import here
import "./ProfileStepOne.css";

const TRANSPARENT_1PX =
  "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII=";

const ProfileStepOne = () => {
  const navigate = useNavigate();

  // Backend field names
  const [bio, setBio] = useState("");
  const [gender, setGender] = useState("");
  const [sexual_preferences, setSexualPreferences] = useState("");
  const [age, setAge] = useState("");
  const [location, setLocation] = useState("");
  const [interests, setInterests] = useState([]);

  const fileInputRef = useRef(null);
  const [status, setStatus] = useState(null);
  const [saving, setSaving] = useState(false);

  const interestOptions = [
    "Hiking","Reading","Cooking","Travel","Music",
    "Art","Sports","Movies","Gaming","Volunteering",
  ];

  const toggleInterest = (item) => {
    setInterests((prev) =>
      prev.includes(item) ? prev.filter((i) => i !== item) : [...prev, item]
    );
  };

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

  const readFirstFileAsBase64 = () =>
    new Promise((resolve) => {
      const file = fileInputRef.current?.files?.[0];
      if (!file) return resolve(null);
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => resolve(null);
      reader.readAsDataURL(file);
    });

  const handleNext = async (e) => {
    e.preventDefault();
    setStatus(null);

    if (!bio.trim()) return setStatus("Please write a short bio.");
    if (!gender) return setStatus("Please select your gender.");
    if (!sexual_preferences) return setStatus("Please select who you are interested in.");
    if (!age || isNaN(Number(age))) return setStatus("Please enter a valid age.");
    if (!location.trim()) return setStatus("Please enter your location.");

    setSaving(true);
    try {
      const base64Image = await readFirstFileAsBase64();
      const pictureToSend = base64Image || TRANSPARENT_1PX;

      const payload = {
        bio,
        gender,
        sexual_preferences,
        age: Number(age),
        location: location.trim(),
        profile_picture: pictureToSend,
        // do NOT include interests here — backend profiles table has no "interests" column
      };

      // 1) Create the profile
      const res = await fetchWithAuth(
        "http://localhost:5000/api/profile/create_profile",
        { method: "POST", body: JSON.stringify(payload) }
      );
      const data = await res.json();
      console.log("create_profile response:", data);

      if (!res.ok) {
        if (Array.isArray(data?.details) && data.details.length) {
          setStatus(`Fix these fields: ${data.details.join(", ")}`);
        } else {
          setStatus(data.error || data.message || "Could not save profile.");
        }
        return;
      }

      // 2) Add interests as tags via /add_tags (only if the user picked some)
      if (interests.length) {
        const tagsRes = await addTags(interests);
        if (!tagsRes.ok) {
          const t = await tagsRes.json().catch(() => ({}));
          console.warn("add_tags failed:", t);
          // We won't block navigation if tag insertion fails
        }
      }

      // 3) Go to dashboard
      navigate("/dashboard");
    } catch (err) {
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
              className={`choice-btn ${gender === opt.value ? "selected" : ""}`}
              onClick={() => setGender(opt.value)}
              type="button"
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
              className={`choice-btn ${sexual_preferences === opt.value ? "selected" : ""}`}
              onClick={() => setSexualPreferences(opt.value)}
              type="button"
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
        ></textarea>

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
            <input
              id="location"
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="City, Country"
            />
          </div>
        </div>

        <h2>What are your interests?</h2>
        <div className="chips-group">
          {interestOptions.map((opt) => (
            <button
              key={opt}
              className={`chip ${interests.includes(opt) ? "selected" : ""}`}
              onClick={() => toggleInterest(opt)}
              type="button"
            >
              {opt}
            </button>
          ))}
        </div>

        <h2>Add photos</h2>
        <p className="photo-hint">Add up to 5 photos, including a profile picture</p>
        <div className="photo-upload">
          <input
            ref={fileInputRef}
            type="file"
            id="fileInput"
            accept="image/*"
            multiple
            style={{ display: "none" }}
          />
          <label htmlFor="fileInput" className="upload-box">
            <p>Upload Photos</p>
            <span>Drag and drop or browse to upload</span>
          </label>
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
