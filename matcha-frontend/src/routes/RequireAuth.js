// src/routes/RequireAuth.jsx
import React, { useEffect } from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { detectAndSendLocation } from "../utils/geolocator";
import { fetchWithAuth } from "../utils/api";

function hasAccessToken() {
  return Boolean(localStorage.getItem("access_token"));
}

export default function RequireAuth() {
  const location = useLocation();

  useEffect(() => {
    // Only run once when user first accesses a protected route
    const locationKey = `location_detected_${localStorage.getItem("access_token")}`;
    const alreadyDetected = sessionStorage.getItem(locationKey);

    if (!alreadyDetected && hasAccessToken()) {
      // Attempt location detection (doesn't block UI)
      detectAndSendLocation(fetchWithAuth)
        .then((result) => {
          if (result.success) {
            console.log(`📍 Location detected from ${result.source}:`, result.location);
            // Mark as detected for this session
            sessionStorage.setItem(locationKey, 'true');
          } else {
            // Only warn if it's not a development environment issue
            if (!result.isDevelopment) {
              console.warn('⚠️ Location detection failed:', result.message);
            }
          }
        })
        .catch((error) => {
          console.warn('⚠️ Location detection error:', error.message);
        });
    }
  }, []);

  if (!hasAccessToken()) {
    return <Navigate to="/signin" replace state={{ from: location }} />;
  }
  
  return <Outlet />;
}

