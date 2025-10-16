// src/utils/authCheck.js

/**
 * Validates if the access token in localStorage is still valid
 * by making a lightweight request to a protected endpoint
 */
export async function validateToken() {
  const token = localStorage.getItem("access_token");
  
  if (!token) {
    return false;
  }

  try {
    const response = await fetch("http://localhost:5000/api/profile/get_profile/me", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      credentials: "include",
    });

    if (response.ok) {
      return true;
    }

    // Token is invalid - clear it
    localStorage.removeItem("access_token");
    window.dispatchEvent(new Event("auth-changed"));
    return false;
  } catch (error) {
    console.error("Token validation failed:", error);
    localStorage.removeItem("access_token");
    window.dispatchEvent(new Event("auth-changed"));
    return false;
  }
}

/**
 * Clear all authentication data
 */
export function clearAuth() {
  localStorage.removeItem("access_token");
  window.dispatchEvent(new Event("auth-changed"));
}
