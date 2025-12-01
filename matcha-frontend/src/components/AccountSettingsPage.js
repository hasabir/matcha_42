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
import { validatePasswordStrength, getPasswordStrength } from "../utils/passwordValidator";
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

const API_BASE = "http://localhost:5000";

/**
 * Convert relative image paths to absolute URLs
 * Handles both /static/profiles/... and /profiles/... (for backward compatibility)
 */
function toAbsoluteUrl(url) {
  if (!url) return null;
  if (/^https?:\/\//i.test(url)) return url;

  let cleanUrl = url.replace(/^\/+/, "");
  
  // If the URL doesn't start with 'static/' but starts with 'profiles/', add 'static/' prefix
  if (cleanUrl.startsWith("profiles/") && !cleanUrl.startsWith("static/")) {
    cleanUrl = `static/${cleanUrl}`;
  }
  
  return `${API_BASE}/${cleanUrl}`;
}

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
  const [profilePicture, setProfilePicture] = useState(null); // Separate state for profile picture
  const [images, setImages] = useState([]); // existing additional images
  const [newProfilePic, setNewProfilePic] = useState(null);
  const [newImages, setNewImages] = useState([]); // files selected for upload
  const [uploadingImages, setUploadingImages] = useState(false);

  // Password fields
  const [currentPwd, setCurrentPwd] = useState("");
  const [newPwd, setNewPwd] = useState("");
  const [confirmPwd, setConfirmPwd] = useState("");
  const [pwdSaving, setPwdSaving] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState({ strength: 'none', color: '#ccc', message: '' });
  const [passwordError, setPasswordError] = useState("");

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
        // 1) Load profile details - using correct endpoint
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
        // Silently handle error
        setStatus("Error loading profile");
      }
      try {
        // 2a) Load profile picture separately
        const picRes = await fetchWithAuth("http://localhost:5000/api/profile/get_profile_pic/me");
        const picData = await picRes.json();
        if (picRes.ok && picData?.result) {
          setProfilePicture(toAbsoluteUrl(picData.result));
        }
      } catch (e) {
        // Silently handle error
      }
      try {
        // 2b) Load additional images
        const imgRes = await fetchWithAuth("http://localhost:5000/api/profile/get_images/me");
        const imgData = await imgRes.json();
        if (imgRes.ok && imgData?.result) {
          // Convert relative paths to absolute URLs
          const imagesWithAbsoluteUrls = imgData.result.map(img => {
            if (typeof img === 'string') {
              return toAbsoluteUrl(img);
            }
            return {
              ...img,
              url: toAbsoluteUrl(img.url || img.image_url)
            };
          });
          setImages(imagesWithAbsoluteUrls);
        }
      } catch (e) {
        // Silently handle error
      }
      try {
        // 3) Load user's tags (interests)
        const tagRes = await fetchWithAuth("http://localhost:5000/api/profile/get_user_tags");
        const tagData = await tagRes.json();
        if (tagRes.ok && tagData?.result) {
          setTags(tagData.result);
        }
      } catch (e) {
        // Silently handle error
      }
      try {
        // 4) Load fame rating (if not already set) and watchers/likers if available
        const fameRes = await fetchWithAuth("http://localhost:5000/api/profile/get_fame_rating");
        const fameData = await fameRes.json();
        if (fameRes.ok) setFameRating(fameData.fame_rating);
      } catch (_) {
        // ignore if endpoint not available
      }
      try {
        // watchers list
        const watchRes = await fetchWithAuth("http://localhost:5000/api/profile/get_profile_visitors");
        const watchData = await watchRes.json();
        if (watchRes.ok && watchData?.result) setWatchers(watchData.result);
      } catch (_) {
        // ignore
      }
      try {
        // likers list
        const likeRes = await fetchWithAuth("http://localhost:5000/api/profile/get_profile_likes");
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
   * Use browser geolocation to set lat/lng/accuracy. On failure the fields
   * remain unchanged. Users can override the text location manually.
   */
  const locateByGPS = async () => {
    if (!navigator.geolocation) {
      setStatus({ type: "error", msg: "❌ Geolocation is not supported by your browser" });
      return;
    }

    // Check permission status first
    try {
      if (navigator.permissions) {
        const permission = await navigator.permissions.query({ name: 'geolocation' });
        
        if (permission.state === 'denied') {
          setStatus({
            type: "error",
            msg: "📍 Location access is blocked. Click the lock icon (🔒) in your address bar and allow location access, then refresh and try again."
          });
          return;
        }
      }
    } catch (e) {
      // Permission API not supported, continue anyway
    }

    setLocating(true);
    setStatus(null);
    
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLat(Number(pos.coords.latitude.toFixed(6)));
        setLng(Number(pos.coords.longitude.toFixed(6)));
        setAccuracy(Math.round(pos.coords.accuracy));
        setLocating(false);
        setStatus({ type: "success", msg: "✅ Location updated successfully" });
      },
      async (error) => {
        setLocating(false);
        
        // Try IP-based fallback automatically
        try {
          const fallbackRes = await fetchWithAuth("http://localhost:5000/api/profile/detect_location", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({})
          });
          
          if (fallbackRes.ok) {
            const fallbackData = await fallbackRes.json();
            if (fallbackData.location) {
              setLocation(fallbackData.location);
              if (fallbackData.latitude && fallbackData.longitude) {
                setLat(Number(fallbackData.latitude));
                setLng(Number(fallbackData.longitude));
                setAccuracy(fallbackData.accuracy || 5000);
              }
              setStatus({
                type: "success",
                msg: "📍 Location detected from your IP address: " + fallbackData.location + " (You can update this manually if needed)"
              });
              return;
            }
          }
        } catch (ipError) {
          // Silently handle IP fallback failure
        }
        
        // If IP fallback also fails, show appropriate message
        let message = "Failed to get your location. ";
        
        switch (error.code) {
          case error.PERMISSION_DENIED:
            message = "📍 Location access denied. We tried to detect from your IP but it didn't work. Click the lock icon (🔒) in your address bar, allow location access, then refresh and try again.";
            break;
          case error.POSITION_UNAVAILABLE:
            message = "❌ Location information is unavailable. Please enter your location manually.";
            break;
          case error.TIMEOUT:
            message = "⏱️ Location request timed out. Please try again.";
            break;
          default:
            message = "❌ An unknown error occurred getting your location.";
        }
        
        setStatus({ type: "error", msg: message });
      },
      { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 }
    );
  };

  /**
   * Update profile information. Sends a PATCH with provided fields to
   * /api/profile/update_profile. Only first and last names are passed
   * separately to the user table; other fields are stored in the profile
   * table. Location and GPS coords are included. After successful
   * update we refetch profile info to display updated fame rating or
   * other derived fields.
   */
  const handleInfoUpdate = async () => {
    setSaving(true);
    setStatus(null);
    try {
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
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data?.error || "Failed to update profile");
      setStatus("✅ Profile updated successfully!");
      
      // refresh all profile data including first_name, last_name, and fame rating
      try {
        const refRes = await fetchWithAuth("http://localhost:5000/api/profile/get_profile/me");
        const refData = await refRes.json();
        if (refRes.ok && refData.result) {
          const profile = refData.result;
          setFirstName(profile.first_name || "");
          setLastName(profile.last_name || "");
          setEmail(profile.email || "");
          setBio(profile.bio || "");
          setGender(profile.gender || "");
          setSexualPreferences(profile.sexual_preferences || "");
          setFameRating(profile.fame_rating);
        }
      } catch (_) {
        // Silently handle refresh failure
      }
      
      // Clear status after 3 seconds
      setTimeout(() => setStatus(null), 3000);
    } catch (e) {
      setStatus(e.message);
    } finally {
      setSaving(false);
    }
  };

  /**
   * Change password for current user. Requires current password and new
   * passwords to match. Uses /api/auth/change_password.
   * Validates password strength before sending to backend.
   * 
   * NOTE: Uses direct fetch instead of fetchWithAuth to prevent automatic
   * redirect on 401 (incorrect current password should show error, not logout)
   */
  const handlePasswordUpdate = async () => {
    // Clear previous errors
    setPasswordError("");
    setStatus(null);
    
    // Validate all fields are filled
    if (!currentPwd || !newPwd || !confirmPwd) {
      const errorMsg = "❌ Please fill in all password fields";
      setPasswordError(errorMsg);
      setStatus(errorMsg);
      return;
    }
    
    // Check if new passwords match
    if (newPwd !== confirmPwd) {
      const errorMsg = "❌ New passwords do not match";
      setPasswordError(errorMsg);
      setStatus(errorMsg);
      return;
    }
    
    // Validate password strength
    const { isValid, error } = validatePasswordStrength(newPwd, "", email);
    if (!isValid) {
      const errorMsg = `❌ ${error}`;
      setPasswordError(errorMsg);
      setStatus(errorMsg);
      return;
    }
    
    setPwdSaving(true);
    
    try {
      // Get access token manually for direct fetch call
      const token = localStorage.getItem("access_token");
      
      // Use direct fetch to prevent automatic redirect on 401
      let res;
      try {
        res = await fetch("http://localhost:5000/api/auth/change_password", {
          method: "POST",
          headers: { 
            "Content-Type": "application/json",
            ...(token ? { "Authorization": `Bearer ${token}` } : {})
          },
          credentials: "include",
          body: JSON.stringify({ current_password: currentPwd, new_password: newPwd }),
        });
      } catch (networkError) {
        // Network error occurred
        const errorMsg = "❌ Unable to change password. Please check your connection and try again.";
        setPasswordError(errorMsg);
        setStatus(errorMsg);
        setPwdSaving(false);
        return;
      }
      
      // Parse JSON response first (before checking res.ok to avoid console errors)
      let data = {};
      try {
        const textResponse = await res.text();
        if (textResponse) {
          data = JSON.parse(textResponse);
        }
      } catch (jsonError) {
        // Silently handle JSON parse errors
        data = {};
      }
      
      // Now check response status and handle errors gracefully
      if (!res.ok) {
        // Handle specific error cases with user-friendly messages
        let errorMessage = data?.error || "Failed to change password";
        
        // Map backend errors to user-friendly messages
        if (res.status === 401) {
          // All 401 errors are incorrect password
          errorMessage = "❌ Current password is incorrect";
        } else if (errorMessage.includes("weak") || errorMessage.includes("common") || 
                   errorMessage.includes("characters") || errorMessage.includes("contain")) {
          errorMessage = `❌ ${data?.error}`;
        } else if (errorMessage.includes("same") || errorMessage.includes("different")) {
          errorMessage = "❌ New password must be different from current password";
        } else {
          errorMessage = "❌ " + errorMessage;
        }
        
        setPasswordError(errorMessage);
        setStatus(errorMessage);
        setPwdSaving(false);
        
        // Silently handle error - no console logging
        return;
      }
      
      // Success!
      setStatus("✅ Password changed successfully!");
      setCurrentPwd("");
      setNewPwd("");
      setConfirmPwd("");
      setPasswordError("");
      setPasswordStrength({ strength: 'none', color: '#ccc', message: '' });
      
      // Clear success message after 3 seconds
      setTimeout(() => setStatus(null), 3000);
      
    } catch (e) {
      // Handle network errors or other exceptions
      const errorMsg = "❌ Unable to change password. Please check your connection and try again.";
      setPasswordError(errorMsg);
      setStatus(errorMsg);
      
      // Silently handle exception - no console logging
    } finally {
      setPwdSaving(false);
    }
  };

  /**
   * Handle new password change and update strength indicator
   */
  const handleNewPasswordChange = (value) => {
    setNewPwd(value);
    setPasswordError("");
    
    if (value) {
      const strength = getPasswordStrength(value);
      setPasswordStrength(strength);
      
      // Validate and show error immediately
      const { isValid, error } = validatePasswordStrength(value, "", email);
      if (!isValid && value.length >= 8) {
        setPasswordError(error);
      }
    } else {
      setPasswordStrength({ strength: 'none', color: '#ccc', message: '' });
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
        method: "PUT",
        body: formData,
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data?.error || "Failed to update profile picture");
      }
      setNewProfilePic(null);
      // Reload profile picture separately
      const picRes = await fetchWithAuth("http://localhost:5000/api/profile/get_profile_pic/me");
      const picData = await picRes.json();
      if (picRes.ok && picData?.result) {
        setProfilePicture(toAbsoluteUrl(picData.result));
      }
      
      // Also reload additional images in case any updates
      const imgRes = await fetchWithAuth("http://localhost:5000/api/profile/get_images/me");
      const imgData = await imgRes.json();
      if (imgRes.ok && imgData?.result) {
        const imagesWithAbsoluteUrls = imgData.result.map(img => {
          if (typeof img === 'string') {
            return toAbsoluteUrl(img);
          }
          return {
            ...img,
            url: toAbsoluteUrl(img.url || img.image_url)
          };
        });
        setImages(imagesWithAbsoluteUrls);
      }
      setStatus("✅ Profile picture updated successfully!");
      
      // Clear status after 3 seconds
      setTimeout(() => setStatus(null), 3000);
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
        // Reload all images to ensure consistency
        const imgRes = await fetchWithAuth("http://localhost:5000/api/profile/get_images/me");
        const imgData = await imgRes.json();
        if (imgRes.ok && imgData?.result) {
          const imagesWithAbsoluteUrls = imgData.result.map(img => {
            if (typeof img === 'string') {
              return toAbsoluteUrl(img);
            }
            return {
              ...img,
              url: toAbsoluteUrl(img.url || img.image_url)
            };
          });
          setImages(imagesWithAbsoluteUrls);
        }
      }
      setNewImages([]);
      setStatus("✅ Images uploaded successfully!");
      
      // Clear status after 3 seconds
      setTimeout(() => setStatus(null), 3000);
    } catch (e) {
      setStatus(`❌ ${e.message}`);
      // Clear status after 5 seconds for errors
      setTimeout(() => setStatus(null), 5000);
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
      if (tagRes.ok && tagData?.result) setTags(tagData.result);
      setStatus("✅ Interest added successfully!");
      
      // Clear status after 3 seconds
      setTimeout(() => setStatus(null), 3000);
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
      if (tagRes.ok && tagData?.result) setTags(tagData.result);
      setStatus("✅ Interest removed successfully!");
      
      // Clear status after 3 seconds
      setTimeout(() => setStatus(null), 3000);
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

        {/* Fame rating only */}
        {fameRating !== null && (
          <div className="fame-section">
            <p className="fame-rating">Fame rating: {fameRating}</p>
          </div>
        )}

        {/* Profile images management */}
        <div className="settings-section">
          <h2>Profile Photo</h2>
          <div className="current-images">
            {profilePicture ? (
              <img
                src={profilePicture}
                alt="Current profile"
                className="profile-thumb"
              />
            ) : (
              <span>No profile picture</span>
            )}
          </div>
          <div className="file-input-wrapper">
            <input
              type="file"
              accept="image/*"
              id="profile-pic-input"
              onChange={(e) => setNewProfilePic(e.target.files?.[0] || null)}
            />
            <label htmlFor="profile-pic-input" className="file-input-label">
              Choose File
            </label>
            <span className="file-name">{newProfilePic?.name || 'No file chosen'}</span>
          </div>
          <div className="actions">
            <button className="update-btn" disabled={!newProfilePic || saving} onClick={updateProfilePicture}>
              Update Profile Picture
            </button>
          </div>
        </div>

        <div className="settings-section">
          <h2>Additional Photos</h2>
          <p className="photo-hint">
            <small>You can upload up to 4 additional photos (5 photos total including profile picture). {images.length}/4 additional photos.</small>
          </p>
          {images.length >= 4 && (
            <p style={{color: '#ff6b6b', fontSize: '14px', marginBottom: '10px'}}>
              ⚠️ Maximum capacity reached. Please delete a photo before uploading a new one.
            </p>
          )}
          <div className="current-images-list">
            {images.length > 0 ? (
              images.map((img, idx) => (
                <img
                  key={idx}
                  src={typeof img === 'string' ? img : (img.url || img.image_url)}
                  alt={`Additional ${idx + 1}`}
                  className="photo-thumb"
                />
              ))
            ) : (
              <span>No additional photos</span>
            )}
          </div>
          <div className="file-input-wrapper">
            <input
              type="file"
              accept="image/*"
              multiple
              id="additional-photos-input"
              onChange={onSelectNewImages}
            />
            <label htmlFor="additional-photos-input" className="file-input-label">
              Choose Files
            </label>
            <span className="file-name">
              {newImages.length > 0 ? `${newImages.length} file(s) selected` : 'No files chosen'}
            </span>
          </div>
          <div className="actions">
            <button
              className="update-btn"
              disabled={newImages.length === 0 || uploadingImages || images.length >= 4}
              onClick={uploadAdditionalImages}
              title={images.length >= 4 ? "Delete a photo first to upload new ones" : ""}
            >
              {uploadingImages ? "Uploading…" : images.length >= 4 ? "Maximum Reached" : "Upload Photos"}
            </button>
          </div>
        </div>

        <div className="settings-section">
          <h2>Change Password</h2>
          <input
            type="password"
            placeholder="Current Password"
            value={currentPwd}
            onChange={(e) => {
              setCurrentPwd(e.target.value);
              setPasswordError("");
            }}
          />
          <input
            type="password"
            placeholder="New Password"
            value={newPwd}
            onChange={(e) => handleNewPasswordChange(e.target.value)}
          />
          {/* Password strength indicator */}
          {newPwd && (
            <div className="password-strength-indicator">
              <div className="strength-bar-container">
                <div 
                  className={`strength-bar strength-${passwordStrength.strength}`}
                  style={{ 
                    width: passwordStrength.strength === 'strong' ? '100%' : 
                           passwordStrength.strength === 'medium' ? '66%' : 
                           passwordStrength.strength === 'weak' ? '33%' : '0%',
                    backgroundColor: passwordStrength.color
                  }}
                />
              </div>
              {passwordStrength.message && (
                <span className="strength-message" style={{ color: passwordStrength.color }}>
                  {passwordStrength.message}
                </span>
              )}
            </div>
          )}
          {/* Show password validation error */}
          {passwordError && newPwd.length >= 3 && (
            <div className="password-error-hint">
              <small style={{ color: '#ff4444' }}>{passwordError}</small>
            </div>
          )}
          <input
            type="password"
            placeholder="Confirm New Password"
            value={confirmPwd}
            onChange={(e) => {
              setConfirmPwd(e.target.value);
              setPasswordError("");
            }}
          />
          <div className="password-requirements">
            <small>
              <strong>Password requirements:</strong> At least 8 characters, containing at least 3 of: uppercase, lowercase, numbers, special characters (!@#$%^&*). Avoid common words and patterns.
            </small>
          </div>
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
                <option value="female">Female</option>
                <option value="male">Male</option>
                <option value="other">Other / Non-binary</option>
              </select>
            </div>
            <div className="inline-field">
              <label>Interested In</label>
              <select value={sexualPreferences} onChange={(e) => setSexualPreferences(e.target.value)}>
                <option value="">Select…</option>
                <option value="female">Women</option>
                <option value="male">Men</option>
                <option value="both">Everyone</option>
              </select>
            </div>
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
                  <button type="button" className="remove-tag-btn" onClick={() => handleRemoveTag(t)} title="Remove">
                    ✕
                  </button>
                </span>
              ))
            ) : (
              <span className="no-interests">No interests yet. Add your hobbies and interests!</span>
            )}
          </div>
          <div className="add-tag-row">
            <input
              type="text"
              placeholder="Add interest"
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
            />
            <button type="button" className="add-tag-btn" disabled={addingTag || !newTag.trim()} onClick={handleAddTag}>
              {addingTag ? "Adding…" : "Add"}
            </button>
          </div>
        </div>

        {status && <p className="status">{status}</p>}
      </div>
    </div>
  );
};

export default AccountSettingsPage;