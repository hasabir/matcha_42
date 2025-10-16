// import React, { useState, useRef, useEffect } from "react";
// import { useNavigate } from "react-router-dom";
// import { fetchWithAuth } from "../utils/api";
// import "./ProfileStepOne.css";

// const ProfileStepOne = () => {
//   const navigate = useNavigate();

//   // Form fields
//   const [bio, setBio] = useState("");
//   const [gender, setGender] = useState("");
//   const [sexualPreferences, setSexualPreferences] = useState("");
//   const [age, setAge] = useState("");
//   const [location, setLocation] = useState("");
//   const [interests, setInterests] = useState([]);

//   // Photos
//   const [photos, setPhotos] = useState([]);
//   const fileInputRef = useRef(null);

//   // Geolocation
//   const [coords, setCoords] = useState({ lat: null, lng: null, acc: null });
//   const [locating, setLocating] = useState(false);

//   // Status
//   const [status, setStatus] = useState(null);
//   const [saving, setSaving] = useState(false);

//   // Options
//   const interestOptions = [
//     "Hiking","Reading","Cooking","Travel","Music","Art",
//     "Sports","Movies","Gaming","Volunteering"
//   ];
//   const genderOptions = [
//     { label: "Female", value: "Female" },
//     { label: "Male", value: "Male" },
//     { label: "Non-binary", value: "Non-binary" },
//     { label: "Other", value: "Other" }
//   ];
//   const sexualPreferenceOptions = [
//     { label: "Women", value: "Women" },
//     { label: "Men", value: "Men" },
//     { label: "Both", value: "Both" },
//     { label: "All", value: "All" }
//   ];

//   // Handle file selection
//   const onPickFiles = (e) => {
//     const files = Array.from(e.target.files || []);
//     const appended = files.map(f => ({ file: f, url: URL.createObjectURL(f), isPrimary: false }));
//     const next = [...photos, ...appended].slice(0,5);
//     if (!next.some(p => p.isPrimary) && next.length>0) next[0].isPrimary = true;
//     setPhotos(next);
//   };

//   const setPrimary = (idx) => {
//     setPhotos(list => list.map((p,i)=>({...p, isPrimary:i===idx})));
//   };

//   const removeAt = (idx) => {
//     setPhotos(list => {
//       const updated = list.filter((_,i)=>i!==idx);
//       if (!updated.some(p=>p.isPrimary) && updated.length>0) updated[0].isPrimary = true;
//       return updated;
//     });
//   };

//   // Geolocation
//   const locateByGPS = () => {
//     if (!("geolocation" in navigator)) return;
//     setLocating(true);
//     navigator.geolocation.getCurrentPosition(
//       pos => {
//         setCoords({ lat:+pos.coords.latitude.toFixed(6), lng:+pos.coords.longitude.toFixed(6), acc:Math.round(pos.coords.accuracy) });
//         setLocating(false);
//       },
//       () => setLocating(false),
//       { enableHighAccuracy:true, timeout:8000, maximumAge:0 }
//     );
//   };

//   useEffect(() => locateByGPS(), []);

//   const toggleInterest = (item) => {
//     setInterests(prev => prev.includes(item) ? prev.filter(i=>i!==item) : [...prev,item]);
//   };

//   // --- Submit handler for full profile flow ---
//   const handleNext = async (e) => {
//     e.preventDefault();
//     setStatus(null);

//     if (!bio.trim()) return setStatus("Please write a short bio.");
//     if (!gender) return setStatus("Please select your gender.");
//     if (!sexualPreferences) return setStatus("Please select your preference.");
//     if (!age || isNaN(Number(age))) return setStatus("Please enter a valid age.");
//     if (!location.trim()) return setStatus("Please enter your location.");

//     setSaving(true);
//     try {
//       const token = localStorage.getItem("access_token");

//       // --- 1) Create profile ---
//       const formData = new FormData();
//       const primaryFile = photos.find(p=>p.isPrimary)?.file;
//       if (primaryFile) formData.append("profile_pic", primaryFile);
//       formData.append("bio", bio);
//       formData.append("gender", gender);
//       formData.append("sexual_preferences", sexualPreferences);
//       formData.append("age", Number(age));

//       const createRes = await fetch("http://localhost:5000/api/profile/create_profile", {
//         method: "POST",
//         headers: { Authorization:`Bearer ${token}` },
//         body: formData
//       });
//       const createData = await createRes.json().catch(()=>({}));
//       if (!createRes.ok) {
//         if (Array.isArray(createData.details) && createData.details.length)
//           setStatus(`Fix these fields: ${createData.details.join(", ")}`);
//         else
//           setStatus(createData.error || "Could not save profile.");
//         setSaving(false); return;
//       }

//       // --- 2) Upload additional images ---
//       const otherFiles = photos.filter(p=>!p.isPrimary).map(p=>p.file);
//       if (otherFiles.length){
//         const uploadForm = new FormData();
//         otherFiles.forEach(f=>uploadForm.append("images", f));
//         await fetch("http://localhost:5000/api/profile/upload_images", {
//           method: "POST",
//           headers:{Authorization:`Bearer ${token}`},
//           body: uploadForm
//         });
//       }

//       // --- 3) Add tags ---
//       if (interests.length){
//         await fetch("http://localhost:5000/api/profile/add_tags", {
//           method:"POST",
//           headers:{Authorization:`Bearer ${token}`, 'Content-Type':'application/json'},
//           body: JSON.stringify({tags: interests})
//         });
//       }

//       // --- 4) Set location (optional) ---
//       if (coords.lat && coords.lng){
//         await fetch("http://localhost:5000/api/profile/set_location", {
//           method:"POST",
//           headers:{Authorization:`Bearer ${token}`, 'Content-Type':'application/json'},
//           body: JSON.stringify({latitude:coords.lat, longitude:coords.lng, accuracy:coords.acc})
//         });
//       }

//       // --- Done ---
//       navigate("/dashboard");

//     } catch(err){
//       console.error(err);
//       setStatus("Network error. Please try again.");
//     } finally {
//       setSaving(false);
//     }
//   };

//   return (
//     <div className="step-container">
//       <div className="step-content">
//         <div className="progress"><span>1 of 5</span><div className="progress-bar"><div className="progress-fill" style={{width:"20%"}}></div></div></div>
//         <h2>What's your gender?</h2>
//         <div className="button-group">{genderOptions.map(opt=>(
//           <button key={opt.value} type="button" className={`choice-btn ${gender===opt.value?"selected":""}`} onClick={()=>setGender(opt.value)}>{opt.label}</button>
//         ))}</div>
//         <h2>Who are you interested in?</h2>
//         <div className="button-group">{sexualPreferenceOptions.map(opt=>(
//           <button key={opt.value} type="button" className={`choice-btn ${sexualPreferences===opt.value?"selected":""}`} onClick={()=>setSexualPreferences(opt.value)}>{opt.label}</button>
//         ))}</div>
//         <h2>Write a bio</h2>
//         <textarea rows="4" placeholder="Tell us about yourself…" className="bio" value={bio} onChange={e=>setBio(e.target.value)}/>
//         <div className="inline-two">
//           <div className="inline-field">
//             <label htmlFor="age">Age</label>
//             <input id="age" type="number" min="18" max="120" value={age} onChange={e=>setAge(e.target.value)} placeholder="e.g., 25"/>
//           </div>
//           <div className="inline-field">
//             <label htmlFor="location">Location</label>
//             <div className="location-row">
//               <input id="location" type="text" value={location} onChange={e=>setLocation(e.target.value)} placeholder="City, Country"/>
//               <button type="button" className="gps-btn" onClick={locateByGPS} disabled={locating}>{locating?"Locating…":"Use my GPS"}</button>
//             </div>
//             {coords.lat && coords.lng && <small className="coords-hint">Detected: {coords.lat}, {coords.lng} (±{coords.acc}m)</small>}
//           </div>
//         </div>
//         <h2>What are your interests?</h2>
//         <div className="chips-group">{interestOptions.map(opt=>(
//           <button key={opt} type="button" className={`chip ${interests.includes(opt)?"selected":""}`} onClick={()=>toggleInterest(opt)}>{opt}</button>
//         ))}</div>
//         <h2>Add photos</h2>
//         <p className="photo-hint">Add up to 5 photos, including a profile picture</p>
//         <input ref={fileInputRef} id="fileInput" type="file" accept="image/*" multiple onChange={onPickFiles} style={{display:"none"}}/>
//         <label htmlFor="fileInput" className="upload-box"><p>Upload Photos</p><span>Drag and drop or browse</span></label>
//         <div className="thumbs">{photos.map((p,i)=>(
//           <div key={i} className={`thumb ${p.isPrimary?"primary":""}`}>
//             <img alt="thumbnail" src={p.url}/>
//             <div className="thumb-actions">
//               <button type="button" onClick={()=>setPrimary(i)}>{p.isPrimary?"Profile Photo":"Set as Profile"}</button>
//               <button type="button" onClick={()=>removeAt(i)}>Remove</button>
//             </div>
//           </div>
//         ))}</div>
//         <button className="next-btn" onClick={handleNext} disabled={saving}>{saving?"Saving…":"Next"}</button>
//         {status && <p className="status">{status}</p>}
//       </div>
//     </div>
//   );
// };

// export default ProfileStepOne;



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

  const interestOptions = [
    "Hiking","Reading","Cooking","Travel","Music","Art",
    "Sports","Movies","Gaming","Volunteering"
  ];
  const genderOptions = [
    { label: "Female", value: "Female" },
    { label: "Male", value: "Male" },
    { label: "Non-binary", value: "Non-binary" },
    { label: "Other", value: "Other" }
  ];
  const sexualPreferenceOptions = [
    { label: "Women", value: "Women" },
    { label: "Men", value: "Men" },
    { label: "Both", value: "Both" },
    { label: "All", value: "All" }
  ];

  const onPickFiles = (e) => {
    const files = Array.from(e.target.files || []);
    
    // Validate file types and sizes
    const validFiles = files.filter(file => {
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
      const maxSize = 5 * 1024 * 1024; // 5MB
      
      if (!validTypes.includes(file.type)) {
        setStatus(`Invalid file type: ${file.name}. Please use JPG, PNG, GIF, or WebP.`);
        return false;
      }
      
      if (file.size > maxSize) {
        setStatus(`File too large: ${file.name}. Maximum size is 5MB.`);
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

  const locateByGPS = () => {
    if (!("geolocation" in navigator)) return;
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      pos => {
        setCoords({
          lat:+pos.coords.latitude.toFixed(6),
          lng:+pos.coords.longitude.toFixed(6),
          acc:Math.round(pos.coords.accuracy)
        });
        setLocating(false);
      },
      () => setLocating(false),
      { enableHighAccuracy:true, timeout:8000, maximumAge:0 }
    );
  };

  useEffect(() => {
    locateByGPS();
    
    // Cleanup function to revoke all object URLs on unmount
    return () => {
      photos.forEach(photo => {
        if (photo?.url) {
          URL.revokeObjectURL(photo.url);
        }
      });
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const toggleInterest = (item) => {
    setInterests(prev => prev.includes(item) ? prev.filter(i => i !== item) : [...prev, item]);
  };

  const handleNext = async (e) => {
    e.preventDefault();
    setStatus(null);

    // Client validation (location is only UI text; coords go to /set_location)
    if (!bio.trim()) return setStatus("Please write a short bio.");
    if (!gender) return setStatus("Please select your gender.");
    if (!sexualPreferences) return setStatus("Please select your preference.");
    if (!age || isNaN(Number(age))) return setStatus("Please enter a valid age.");
    if (!location.trim()) return setStatus("Please enter your location.");

    setSaving(true);
    try {
      const token = localStorage.getItem("access_token");

      // 1) create profile
      const formData = new FormData();
      const primaryFile = photos.find(p=>p.isPrimary)?.file;
      if (primaryFile) formData.append("profile_pic", primaryFile);
      formData.append("bio", bio);
      formData.append("gender", gender);
      formData.append("sexual_preferences", sexualPreferences);
      formData.append("age", Number(age));

      const createRes = await fetch("http://localhost:5000/api/profile/create_profile", {
        method: "POST",
        headers: { Authorization:`Bearer ${token}` },
        body: formData
      });
      const createData = await createRes.json().catch(()=>({}));
      if (!createRes.ok) {
        if (Array.isArray(createData.details) && createData.details.length) {
          setStatus(`Fix these fields: ${createData.details.join(", ")}`);
        } else {
          setStatus(createData.error || "Could not save profile.");
        }
        setSaving(false);
        return;
      }

      // 2) upload extra images
      const others = photos.filter(p=>!p.isPrimary).map(p=>p.file);
      if (others.length) {
        const uploadForm = new FormData();
        others.forEach(f => uploadForm.append("images", f));
        await fetch("http://localhost:5000/api/profile/upload_images", {
          method: "POST",
          headers: { Authorization:`Bearer ${token}` },
          body: uploadForm
        });
      }

      // 3) add tags
      if (interests.length) {
        await fetch("http://localhost:5000/api/profile/add_tags", {
          method: "POST",
          headers: { Authorization:`Bearer ${token}`, "Content-Type":"application/json" },
          body: JSON.stringify({ tags: interests })
        });
      }

      // 4) set location with coordinates (optional)
      if (coords.lat && coords.lng) {
        await fetch("http://localhost:5000/api/profile/set_location", {
          method: "POST",
          headers: { Authorization:`Bearer ${token}`, "Content-Type":"application/json" },
          body: JSON.stringify({ latitude: coords.lat, longitude: coords.lng, accuracy: coords.acc })
        });
      }

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
        <div className="progress">
          <span>1 of 5</span>
          <div className="progress-bar"><div className="progress-fill" style={{width:"20%"}}/></div>
        </div>

        <h2>What's your gender?</h2>
        <div className="button-group">
          {genderOptions.map(opt=>(
            <button key={opt.value} type="button"
              className={`choice-btn ${gender===opt.value?"selected":""}`}
              onClick={()=>setGender(opt.value)}>{opt.label}</button>
          ))}
        </div>

        <h2>Who are you interested in?</h2>
        <div className="button-group">
          {sexualPreferenceOptions.map(opt=>(
            <button key={opt.value} type="button"
              className={`choice-btn ${sexualPreferences===opt.value?"selected":""}`}
              onClick={()=>setSexualPreferences(opt.value)}>{opt.label}</button>
          ))}
        </div>

        <h2>Write a bio</h2>
        <textarea rows="4" placeholder="Tell us about yourself…"
          className="bio" value={bio} onChange={e=>setBio(e.target.value)} />

        <div className="inline-two">
          <div className="inline-field">
            <label htmlFor="age">Age</label>
            <input id="age" type="number" min="18" max="120"
              value={age} onChange={e=>setAge(e.target.value)} placeholder="e.g., 25" />
          </div>
          <div className="inline-field">
            <label htmlFor="location">Location</label>
            <div className="location-row">
              <input id="location" type="text" value={location}
                onChange={e=>setLocation(e.target.value)} placeholder="City, Country" />
              <button type="button" className="gps-btn"
                onClick={locateByGPS} disabled={locating}>
                {locating ? "Locating…" : "Use my GPS"}
              </button>
            </div>
            {coords.lat && coords.lng && (
              <small className="coords-hint">Detected: {coords.lat}, {coords.lng} (±{coords.acc}m)</small>
            )}
          </div>
        </div>

        <h2>What are your interests?</h2>
        <div className="chips-group">
          {["Hiking","Reading","Cooking","Travel","Music","Art","Sports","Movies","Gaming","Volunteering"].map(opt=>(
            <button key={opt} type="button"
              className={`chip ${interests.includes(opt)?"selected":""}`}
              onClick={()=>toggleInterest(opt)}>{opt}</button>
          ))}
        </div>

        <h2>Add photos</h2>
        <p className="photo-hint">
          Add up to 5 photos (JPG, PNG, GIF, or WebP). Max 5MB per file.
          {photos.length > 0 && ` (${photos.length}/5 photos added)`}
        </p>
        <input 
          ref={fileInputRef} 
          id="fileInput" 
          type="file" 
          accept="image/jpeg,image/jpg,image/png,image/gif,image/webp" 
          multiple
          onChange={onPickFiles} 
          style={{ display:"none" }} 
        />
        <label htmlFor="fileInput" className="upload-box">
          <p>📸 Upload Photos</p>
          <span>Click to browse or drag and drop images here</span>
        </label>

        {photos.length > 0 && (
          <div className="thumbs">
            {photos.map((p, i) => (
              <div key={`photo-${i}-${p.file?.name}`} className={`thumb ${p.isPrimary ? "primary" : ""}`}>
                <img 
                  alt={`Photo ${i + 1}`} 
                  src={p.url} 
                  onError={(e) => {
                    console.error('Image load error:', p.url);
                    e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect fill="%23ddd" width="100" height="100"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23999"%3EError%3C/text%3E%3C/svg%3E';
                  }}
                />
                {p.isPrimary && <span className="primary-badge">Profile Photo</span>}
                <div className="thumb-actions">
                  <button type="button" onClick={() => setPrimary(i)}>
                    {p.isPrimary ? "✓ Profile Photo" : "Set as Profile"}
                  </button>
                  <button type="button" onClick={() => removeAt(i)}>✕ Remove</button>
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
