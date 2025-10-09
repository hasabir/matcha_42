// import React, { useEffect, useState } from "react";
// import { fetchWithAuth } from "../utils/api";
// import "./AccountSettingsPage.css";

// const AccountSettingsPage = () => {
//   // profile fields
//   const [first_name, setFirstName] = useState("");
//   const [last_name, setLastName] = useState("");
//   const [email, setEmail] = useState("");
//   const [bio, setBio] = useState("");
//   const [gender, setGender] = useState("");
//   const [sexual_preferences, setSexualPreferences] = useState("");
//   const [location, setLocation] = useState("");

//   // password
//   const [currentPwd, setCurrentPwd] = useState("");
//   const [newPwd, setNewPwd] = useState("");
//   const [confirmPwd, setConfirmPwd] = useState("");

//   const [status, setStatus] = useState(null);
//   const [loading, setLoading] = useState(true);
//   const [saving, setSaving] = useState(false);
//   const [pwdSaving, setPwdSaving] = useState(false);

//   useEffect(() => {
//     const load = async () => {
//       setLoading(true);
//       setStatus(null);
//       try {
//         const res = await fetchWithAuth("http://localhost:5000/api/profile/me");
//         const data = await res.json();
//         if (!res.ok) throw new Error(data?.error || "Failed to load profile");

//         setFirstName(data.first_name || "");
//         setLastName(data.last_name || "");
//         setEmail(data.email || "");
//         setBio(data.bio || "");
//         setGender(data.gender || "");
//         setSexualPreferences(data.sexual_preferences || "");
//         setLocation(data.location || "");
//       } catch (e) {
//         setStatus(e.message);
//       } finally {
//         setLoading(false);
//       }
//     };
//     load();
//   }, []);

//   const handleInfoUpdate = async () => {
//     setSaving(true);
//     setStatus(null);
//     try {
//       const res = await fetchWithAuth("http://localhost:5000/api/profile/me", {
//         method: "PATCH",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({
//           first_name,
//           last_name,
//           email,
//           bio,
//           gender,
//           sexual_preferences,
//           location,
//         }),
//       });
//       const data = await res.json().catch(() => ({}));
//       if (!res.ok) throw new Error(data?.error || "Failed to update profile");
//       setStatus("Profile updated.");
//     } catch (e) {
//       setStatus(e.message);
//     } finally {
//       setSaving(false);
//     }
//   };

//   const handlePasswordUpdate = async () => {
//     if (!currentPwd || !newPwd) return setStatus("Fill all password fields.");
//     if (newPwd !== confirmPwd) return setStatus("New passwords do not match.");
//     setPwdSaving(true);
//     setStatus(null);
//     try {
//       const res = await fetchWithAuth("http://localhost:5000/api/auth/change_password", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({
//           current_password: currentPwd,
//           new_password: newPwd,
//         }),
//       });
//       const data = await res.json().catch(() => ({}));
//       if (!res.ok) throw new Error(data?.error || "Failed to change password");
//       setStatus("Password changed.");
//       setCurrentPwd(""); setNewPwd(""); setConfirmPwd("");
//     } catch (e) {
//       setStatus(e.message);
//     } finally {
//       setPwdSaving(false);
//     }
//   };

//   if (loading) {
//     return (
//       <div className="account-settings-container">
//         <div className="settings-content"><p>Loading…</p></div>
//       </div>
//     );
//   }

//   return (
//     <div className="account-settings-container">
//       <div className="settings-content">
//         <button className="back-btn" onClick={() => window.history.back()}>
//           Back
//         </button>
//         <h1>Account Settings</h1>

//         <div className="settings-section">
//           <h2>Change Password</h2>
//           <input
//             type="password"
//             placeholder="Current Password"
//             value={currentPwd}
//             onChange={(e) => setCurrentPwd(e.target.value)}
//           />
//           <input
//             type="password"
//             placeholder="New Password"
//             value={newPwd}
//             onChange={(e) => setNewPwd(e.target.value)}
//           />
//           <input
//             type="password"
//             placeholder="Confirm New Password"
//             value={confirmPwd}
//             onChange={(e) => setConfirmPwd(e.target.value)}
//           />
//           <div className="actions">
//             <button className="update-btn" disabled={pwdSaving} onClick={handlePasswordUpdate}>
//               {pwdSaving ? "Saving…" : "Update Password"}
//             </button>
//           </div>
//         </div>

//         <div className="settings-section">
//           <h2>Personal Information</h2>
//           <input
//             type="text"
//             placeholder="First name"
//             value={first_name}
//             onChange={(e) => setFirstName(e.target.value)}
//           />
//           <input
//             type="text"
//             placeholder="Last name"
//             value={last_name}
//             onChange={(e) => setLastName(e.target.value)}
//           />
//           <input
//             type="email"
//             placeholder="Email"
//             value={email}
//             onChange={(e) => setEmail(e.target.value)}
//           />

//           <textarea
//             rows="3"
//             placeholder="Biography"
//             value={bio}
//             onChange={(e) => setBio(e.target.value)}
//           />

//           <div className="inline-two">
//             <div className="inline-field">
//               <label>Gender</label>
//               <select value={gender} onChange={(e) => setGender(e.target.value)}>
//                 <option value="">Select…</option>
//                 <option value="Female">Female</option>
//                 <option value="Male">Male</option>
//                 <option value="Non-binary">Non-binary</option>
//                 <option value="Other">Other</option>
//               </select>
//             </div>
//             <div className="inline-field">
//               <label>Interested In</label>
//               <select
//                 value={sexual_preferences}
//                 onChange={(e) => setSexualPreferences(e.target.value)}
//               >
//                 <option value="">Select…</option>
//                 <option value="Women">Women</option>
//                 <option value="Men">Men</option>
//                 <option value="Both">Both</option>
//                 <option value="All">All</option>
//               </select>
//             </div>
//           </div>

//           <input
//             type="text"
//             placeholder="Location"
//             value={location}
//             onChange={(e) => setLocation(e.target.value)}
//           />

//           <div className="actions">
//             <button className="update-btn" disabled={saving} onClick={handleInfoUpdate}>
//               {saving ? "Saving…" : "Update Information"}
//             </button>
//           </div>
//         </div>

//         {/* Dummy notification prefs kept, you can wire later */}
//         <div className="settings-section">
//           <h2>Notification Preferences</h2>
//           <div className="checkbox-group">
//             <label><input type="checkbox" /> <span>New Matches</span></label>
//             <label><input type="checkbox" /> <span>Messages</span></label>
//             <label><input type="checkbox" /> <span>Profile Updates</span></label>
//           </div>
//           <div className="actions">
//             <button className="update-btn">Save Preferences</button>
//           </div>
//         </div>

//         {status && <p className="status">{status}</p>}
//       </div>
//     </div>
//   );
// };

// export default AccountSettingsPage;
import React, { useEffect, useState } from "react";
import { fetchWithAuth } from "../utils/api";
import "./AccountSettingsPage.css";

/**
 * AccountSettingsPage allows a signed-in user to view and update their
 * personal information, including first/last name, email, bio, gender,
 * sexual preferences, location and coordinates, and interests. Users can
 * change their password, upload a new profile picture, upload additional
 * photos, add or remove interests and view their fame rating. Where
 * possible we load current data from the backend using the provided
 * endpoints (e.g. /api/profile/me, /api/profile/get_my_images). Some
 * features like "who viewed my profile" and "who liked me" require
 * backend support and will be shown as placeholders if those endpoints
 * are not available.
 */

const AccountSettingsPage = () => {
  // Basic profile fields
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [bio, setBio] = useState("");
  const [gender, setGender] = useState("");
  const [sexualPreferences, setSexualPreferences] = useState("");
  const [location, setLocation] = useState("");

  // Coordinates (GPS)
  const [lat, setLat] = useState(null);
  const [lng, setLng] = useState(null);
  const [accuracy, setAccuracy] = useState(null);
  const [locating, setLocating] = useState(false);

  // Interests (tags)
  const [tags, setTags] = useState([]); // list of existing tag strings
  const [newTag, setNewTag] = useState("");
  const [addingTag, setAddingTag] = useState(false);

  // Images
  const [images, setImages] = useState([]); // existing images { id, url }
  const [newProfilePic, setNewProfilePic] = useState(null);
  const [newImages, setNewImages] = useState([]); // files selected for upload
  const [uploadingImages, setUploadingImages] = useState(false);

  // Password fields
  const [currentPwd, setCurrentPwd] = useState("");
  const [newPwd, setNewPwd] = useState("");
  const [confirmPwd, setConfirmPwd] = useState("");
  const [pwdSaving, setPwdSaving] = useState(false);

  // Fame rating and social signals
  const [fameRating, setFameRating] = useState(null);
  const [watchers, setWatchers] = useState([]);
  const [likers, setLikers] = useState([]);

  // UI state
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  /**
   * Fetch current profile information, images, tags and fame/social
   * indicators on mount. If endpoints are missing or fail, we
   * gracefully ignore the error.
   */
  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setStatus(null);
      try {
        // 1) Load profile details - FIXED: use correct endpoint
        const res = await fetchWithAuth("http://localhost:5000/api/profile/get_profile/me");
        const data = await res.json();
        if (res.ok && data.result) {
          const profile = data.result;
          setFirstName(profile.first_name || "");
          setLastName(profile.last_name || "");
          setEmail(profile.email || "");
          setBio(profile.bio || "");
          setGender(profile.gender || "");
          setSexualPreferences(profile.sexual_preferences || "");
          setLocation(profile.location || "");
          setLat(profile.lat ?? null);
          setLng(profile.lng ?? null);
          setAccuracy(profile.accuracy ?? null);
          if (profile.fame_rating !== undefined) setFameRating(profile.fame_rating);
        }
      } catch (e) {
        console.warn("Failed to load profile", e);
        setStatus("Error loading profile");
      }
      try {
        // 2) Load user's images - use "me" endpoint
        const imgRes = await fetchWithAuth("http://localhost:5000/api/profile/get_images/me");
        const imgData = await imgRes.json();
        if (imgRes.ok && imgData?.result) {
          // result is array of image URLs
          setImages(Array.isArray(imgData.result) ? imgData.result.map(url => ({ url })) : []);
        }
      } catch (e) {
        console.warn("Failed to load images", e);
      }
      try {
        // 3) Load user's tags (interests)
        const tagRes = await fetchWithAuth("http://localhost:5000/api/profile/get_user_tags");
        const tagData = await tagRes.json();
        if (tagRes.ok && tagData?.result) {
          setTags(tagData.result.map((t) => t.tag || t));
        }
      } catch (e) {
        console.warn("Failed to load tags", e);
      }
      try {
        // 4) Load fame rating
        const fameRes = await fetchWithAuth("http://localhost:5000/api/profile/get_fame_rating");
        const fameData = await fameRes.json();
        if (fameRes.ok && fameData.fame_rating !== undefined) {
          setFameRating(fameData.fame_rating);
        }
      } catch (_) {
        // ignore if endpoint not available
      }
      try {
        // watchers list
        const watchRes = await fetchWithAuth("http://localhost:5000/api/profile/get_profile_vistors");
        const watchData = await watchRes.json();
        if (watchRes.ok && watchData?.result) setWatchers(watchData.result);
      } catch (_) {
        // ignore
      }
      try {
        // likers list - use interactions API
        const likeRes = await fetchWithAuth("http://localhost:5000/api/interactions/get_users/likers");
        const likeData = await likeRes.json();
        if (likeRes.ok && likeData?.result) setLikers(likeData.result);
      } catch (_) {
        // ignore
      }
      setLoading(false);
    };
    load();
  }, []);

  /**
   * Use browser geolocation to set lat/lng/accuracy and immediately sync
   * with backend. On failure the fields remain unchanged.
   */
  const locateByGPS = async () => {
    if (!navigator.geolocation) {
      setStatus("Geolocation is not supported by your browser");
      return;
    }
    
    setLocating(true);
    setStatus(null);
    
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const latitude = Number(pos.coords.latitude.toFixed(6));
        const longitude = Number(pos.coords.longitude.toFixed(6));
        const gpsAccuracy = Math.round(pos.coords.accuracy);
        
        setLat(latitude);
        setLng(longitude);
        setAccuracy(gpsAccuracy);
        
        // Immediately sync GPS coordinates with backend
        try {
          const locRes = await fetchWithAuth("http://localhost:5000/api/profile/set_location", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              latitude,
              longitude,
              accuracy: gpsAccuracy,
            }),
          });
          
          if (locRes.ok) {
            setStatus("GPS location updated successfully!");
          } else {
            const locData = await locRes.json().catch(() => ({}));
            throw new Error(locData?.error || "Failed to sync GPS location");
          }
        } catch (err) {
          console.error("GPS sync error:", err);
          setStatus("GPS detected but failed to sync with server");
        } finally {
          setLocating(false);
        }
      },
      (error) => {
        setLocating(false);
        setStatus(`GPS error: ${error.message}`);
      },
      { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 }
    );
  };

  /**
   * Update profile information. Sends a POST with provided fields to
   * /api/profile/update_profile. First and last names update the user table,
   * other fields update the profile table. GPS coordinates are sent separately
   * to /api/profile/set_location if available.
   */
  const handleInfoUpdate = async () => {
    setSaving(true);
    setStatus(null);
    try {
      // 1) Update profile info (without GPS coords)
      const res = await fetchWithAuth("http://localhost:5000/api/profile/update_profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastName,
          email,
          bio,
          gender,
          sexual_preferences: sexualPreferences,
          location, // text location only
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data?.error || "Failed to update profile");

      // 2) If GPS coordinates are available, send them to set_location endpoint
      if (lat !== null && lng !== null) {
        try {
          const locRes = await fetchWithAuth("http://localhost:5000/api/profile/set_location", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              latitude: lat,
              longitude: lng,
              accuracy: accuracy || 50,
            }),
          });
          if (!locRes.ok) {
            console.warn("Failed to update GPS location");
          }
        } catch (locErr) {
          console.warn("Location update error:", locErr);
        }
      }

      setStatus("Profile updated.");
      
      // 3) Refresh fame rating
      try {
        const refRes = await fetchWithAuth("http://localhost:5000/api/profile/get_profile/me");
        const refData = await refRes.json();
        if (refRes.ok && refData.result) {
          setFameRating(refData.result.fame_rating);
        }
      } catch (_) {}
      
    } catch (e) {
      setStatus(e.message);
    } finally {
      setSaving(false);
    }
  };

  /**
   * Change password for current user. Requires current password and new
   * passwords to match. Uses /api/auth/change_password.
   */
  const handlePasswordUpdate = async () => {
    if (!currentPwd || !newPwd) return setStatus("Fill all password fields.");
    if (newPwd !== confirmPwd) return setStatus("New passwords do not match.");
    setPwdSaving(true);
    setStatus(null);
    try {
      const res = await fetchWithAuth("http://localhost:5000/api/auth/change_password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ current_password: currentPwd, new_password: newPwd }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data?.error || "Failed to change password");
      setStatus("Password changed.");
      setCurrentPwd("");
      setNewPwd("");
      setConfirmPwd("");
    } catch (e) {
      setStatus(e.message);
    } finally {
      setPwdSaving(false);
    }
  };

  /**
   * Update the primary profile picture. This wraps /api/profile/update_profile_picture
   * and sends a file with key 'profile_pic'. On success we refetch images.
   */
  const updateProfilePicture = async () => {
    if (!newProfilePic) return;
    const formData = new FormData();
    formData.append("profile_pic", newProfilePic);
    try {
      setSaving(true);
      const res = await fetchWithAuth("http://localhost:5000/api/profile/update_profile_picture", {
        method: "PUT", // Backend expects PUT method
        body: formData,
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data?.error || "Failed to update profile picture");
      }
      setNewProfilePic(null);
      // reload images - FIXED: use correct endpoint
      const imgRes = await fetchWithAuth("http://localhost:5000/api/profile/get_images/me");
      const imgData = await imgRes.json();
      if (imgRes.ok && imgData?.result) {
        setImages(Array.isArray(imgData.result) ? imgData.result.map(url => ({ url })) : []);
      }
      setStatus("Profile picture updated.");
    } catch (e) {
      setStatus(e.message);
    } finally {
      setSaving(false);
    }
  };

  /**
   * Upload additional images. We send a FormData with key 'images'
   * containing one or more files. After successful upload we append
   * returned image paths to the images list.
   */
  const uploadAdditionalImages = async () => {
    if (newImages.length === 0) return;
    const formData = new FormData();
    newImages.forEach((file) => formData.append("images", file));
    try {
      setUploadingImages(true);
      const res = await fetchWithAuth("http://localhost:5000/api/profile/upload_images", {
        method: "POST",
        body: formData,
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data?.error || "Failed to upload images");
      if (data?.image_paths) {
        // Append to existing images list
        setImages((prev) => [...prev, ...data.image_paths.map((p) => ({ url: p }))]);
      }
      setNewImages([]);
      setStatus("Images uploaded.");
    } catch (e) {
      setStatus(e.message);
    } finally {
      setUploadingImages(false);
    }
  };

  /**
   * Add a new interest tag. Calls /api/profile/add_tags with a list
   * containing the new tag. After success we refresh tags.
   */
  const handleAddTag = async () => {
    const tag = newTag.trim();
    if (!tag) return;
    setAddingTag(true);
    setStatus(null);
    try {
      const res = await fetchWithAuth("http://localhost:5000/api/profile/add_tags", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tags: [tag] }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data?.error || "Failed to add tag");
      setNewTag("");
      // reload tags
      const tagRes = await fetchWithAuth("http://localhost:5000/api/profile/get_user_tags");
      const tagData = await tagRes.json();
      if (tagRes.ok && tagData?.result) setTags(tagData.result.map((t) => t.tag));
      setStatus("Tag added.");
    } catch (e) {
      setStatus(e.message);
    } finally {
      setAddingTag(false);
    }
  };

  /**
   * Remove an existing tag by calling /api/profile/delete_tag with
   * { tag: <string> }. After success we refresh tags.
   */
  const handleRemoveTag = async (tag) => {
    try {
      const res = await fetchWithAuth("http://localhost:5000/api/profile/delete_tag", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tag }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data?.error || "Failed to remove tag");
      // reload tags
      const tagRes = await fetchWithAuth("http://localhost:5000/api/profile/get_user_tags");
      const tagData = await tagRes.json();
      if (tagRes.ok && tagData?.result) setTags(tagData.result.map((t) => t.tag));
      setStatus("Tag removed.");
    } catch (e) {
      setStatus(e.message);
    }
  };

  /**
   * Handler for selecting new images for upload. Stores the files in
   * newImages state. We don't preview them here but they will upload
   * when the user clicks the upload button.
   */
  const onSelectNewImages = (e) => {
    const files = Array.from(e.target.files || []);
    setNewImages(files);
  };

  if (loading) {
    return (
      <div className="account-settings-container">
        <div className="settings-content"><p>Loading…</p></div>
      </div>
    );
  }

  return (
    <div className="account-settings-container">
      <div className="settings-content">
        <button className="back-btn" onClick={() => window.history.back()}>
          Back
        </button>
        <h1>Account Settings</h1>

        {/* Fame rating & social stats */}
        <div className="fame-section">
          {fameRating !== null && (
            <p className="fame-rating">Fame rating: {fameRating}</p>
          )}
          <p className="social-stats">
            {watchers.length} view{watchers.length === 1 ? "" : "s"}, {likers.length} like
            {likers.length === 1 ? "" : "s"}
          </p>
        </div>

        {/* Profile images management */}
        <div className="settings-section">
          <h2>Profile Photo</h2>
          <div className="current-images">
            {images.length > 0 ? (
              <img
                src={images[0].url || images[0]}
                alt="Current profile"
                className="profile-thumb"
              />
            ) : (
              <span>No profile picture</span>
            )}
          </div>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setNewProfilePic(e.target.files?.[0] || null)}
          />
          <div className="actions">
            <button className="update-btn" disabled={!newProfilePic || saving} onClick={updateProfilePicture}>
              Update Profile Picture
            </button>
          </div>
        </div>

        <div className="settings-section">
          <h2>Additional Photos</h2>
          <div className="current-images-list">
            {images.slice(1).length > 0 ? (
              images.slice(1).map((img, idx) => (
                <img
                  key={idx}
                  src={img.url || img}
                  alt={`Photo ${idx + 2}`}
                  className="photo-thumb"
                />
              ))
            ) : (
              <span>No additional photos</span>
            )}
          </div>
          <input
            type="file"
            accept="image/*"
            multiple
            onChange={onSelectNewImages}
          />
          <div className="actions">
            <button
              className="update-btn"
              disabled={newImages.length === 0 || uploadingImages}
              onClick={uploadAdditionalImages}
            >
              {uploadingImages ? "Uploading…" : "Upload Photos"}
            </button>
          </div>
        </div>

        <div className="settings-section">
          <h2>Change Password</h2>
          <input
            type="password"
            placeholder="Current Password"
            value={currentPwd}
            onChange={(e) => setCurrentPwd(e.target.value)}
          />
          <input
            type="password"
            placeholder="New Password"
            value={newPwd}
            onChange={(e) => setNewPwd(e.target.value)}
          />
          <input
            type="password"
            placeholder="Confirm New Password"
            value={confirmPwd}
            onChange={(e) => setConfirmPwd(e.target.value)}
          />
          <div className="actions">
            <button className="update-btn" disabled={pwdSaving} onClick={handlePasswordUpdate}>
              {pwdSaving ? "Saving…" : "Update Password"}
            </button>
          </div>
        </div>

        <div className="settings-section">
          <h2>Personal Information</h2>
          <input
            type="text"
            placeholder="First name"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
          />
          <input
            type="text"
            placeholder="Last name"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
          />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <textarea
            rows="3"
            placeholder="Biography"
            value={bio}
            onChange={(e) => setBio(e.target.value)}
          />

          <div className="inline-two">
            <div className="inline-field">
              <label>Gender</label>
              <select value={gender} onChange={(e) => setGender(e.target.value)}>
                <option value="">Select…</option>
                <option value="Female">Female</option>
                <option value="Male">Male</option>
                <option value="Non-binary">Non-binary</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div className="inline-field">
              <label>Interested In</label>
              <select value={sexualPreferences} onChange={(e) => setSexualPreferences(e.target.value)}>
                <option value="">Select…</option>
                <option value="Women">Women</option>
                <option value="Men">Men</option>
                <option value="Both">Both</option>
                <option value="All">All</option>
              </select>
            </div>
          </div>

          <label htmlFor="location-input">Location (City, Country)</label>
          <input
            id="location-input"
            type="text"
            placeholder="e.g., Paris, France"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          />
          
          <label>GPS Coordinates (for matching nearby users)</label>
          <div className="coords-group">
            <button type="button" className="gps-btn" onClick={locateByGPS} disabled={locating}>
              {locating ? "Locating…" : "Use my GPS"}
            </button>
            {lat && lng && (
              <small className="coords-hint">
                {lat}, {lng} (±{accuracy}m)
              </small>
            )}
          </div>

          <div className="actions">
            <button className="update-btn" disabled={saving} onClick={handleInfoUpdate}>
              {saving ? "Saving…" : "Update Information"}
            </button>
          </div>
        </div>

        <div className="settings-section">
          <h2>Interests</h2>
          <div className="tag-list">
            {tags.length > 0 ? (
              tags.map((t, i) => (
                <span key={i} className="tag-item">
                  {t}
                  <button type="button" onClick={() => handleRemoveTag(t)} title="Remove">
                    ✕
                  </button>
                </span>
              ))
            ) : (
              <span>No interests yet.</span>
            )}
          </div>
          <div className="add-tag-row">
            <input
              type="text"
              placeholder="Add interest"
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
            />
            <button type="button" disabled={addingTag} onClick={handleAddTag}>
              {addingTag ? "Adding…" : "Add"}
            </button>
          </div>
        </div>

        {/* Notification preferences placeholder */}
        <div className="settings-section">
          <h2>Notification Preferences</h2>
          <div className="checkbox-group">
            <label>
              <input type="checkbox" /> <span>New Matches</span>
            </label>
            <label>
              <input type="checkbox" /> <span>Messages</span>
            </label>
            <label>
              <input type="checkbox" /> <span>Profile Updates</span>
            </label>
          </div>
          <div className="actions">
            <button className="update-btn">Save Preferences</button>
          </div>
        </div>

        {status && <p className="status">{status}</p>}
      </div>
    </div>
  );
};

export default AccountSettingsPage;