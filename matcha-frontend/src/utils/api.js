// src/utils/api.js

export const BASE = "http://localhost:5000";

/**
 * fetchWithAuth
 * - Attaches Authorization: Bearer <access_token> if present
 * - On 401/403 tries a one-time refresh via POST /api/auth/refresh (cookie-based)
 * - Retries the original request with the new access token
 * - Redirects to /signin if refresh fails or retry is still unauthorized
 * - Does NOT redirect for blocked user 403s (business logic, not auth error)
 *
 * NOTE:
 *  • Do NOT set "Content-Type" here (some calls send FormData).
 *  • Callers set headers as needed.
 */
export async function fetchWithAuth(url, options = {}) {
  const initialToken = localStorage.getItem("access_token");

  const baseHeaders = {
    ...(options.headers || {}),
    ...(initialToken ? { Authorization: `Bearer ${initialToken}` } : {}),
  };

  // First attempt
  let res = await fetch(url, {
    ...options,
    headers: baseHeaders,
    credentials: "include", // so /api/auth/refresh can read the httpOnly cookie
  });

  // Success or any non-auth error → return immediately
  if (res.status !== 401 && res.status !== 403) return res;

  // Check if 403 is due to blocked user (business logic, not auth error)
  if (res.status === 403) {
    try {
      // Clone response to read body without consuming it
      const clonedRes = res.clone();
      const errorData = await clonedRes.json().catch(() => ({}));
      const errorMessage = errorData.error || "";
      
      // Check if this is a blocked user error (not an auth error)
      if (
        errorMessage.includes("blocked") ||
        errorMessage.includes("You are blocked") ||
        errorMessage.includes("You have blocked")
      ) {
        // This is a blocked user error, not an auth error - return it without redirecting
        return res;
      }
    } catch (e) {
      // If we can't parse the response, continue with auth refresh logic
    }
  }

  // Attempt refresh
  const refreshRes = await fetch(`${BASE}/api/auth/refresh`, {
    method: "POST",
    credentials: "include",
  });

  if (!refreshRes.ok) {
    // Refresh failed → force sign-in
    window.location.href = "/signin";
    return res;
  }

  const { access_token } = await refreshRes.json().catch(() => ({}));
  if (!access_token) {
    window.location.href = "/signin";
    return res;
  }

  // Persist and retry original request
  localStorage.setItem("access_token", access_token);

  const retryHeaders = {
    ...(options.headers || {}),
    Authorization: `Bearer ${access_token}`,
  };

  res = await fetch(url, {
    ...options,
    headers: retryHeaders,
    credentials: "include",
  });

  // If still unauthorized, check if it's a blocked user error
  if (res.status === 401 || res.status === 403) {
    // Check if 403 is due to blocked user
    if (res.status === 403) {
      try {
        const clonedRes = res.clone();
        const errorData = await clonedRes.json().catch(() => ({}));
        const errorMessage = errorData.error || "";
        
        if (
          errorMessage.includes("blocked") ||
          errorMessage.includes("You are blocked") ||
          errorMessage.includes("You have blocked")
        ) {
          // This is a blocked user error, not an auth error - return it without redirecting
          return res;
        }
      } catch (e) {
        // If we can't parse the response, treat as auth error
      }
    }
    
    // Only redirect if it's a real auth error (401 or non-blocked 403)
    window.location.href = "/signin";
  }

  return res;
}

/* =========================
 *  Profile / Location APIs
 * ========================= */

export const api = {
  meProfile: (options = {}) =>
    fetchWithAuth(`${BASE}/api/profile/get_profile/me`, options),

  userProfile: (username, options = {}) =>
    fetchWithAuth(`${BASE}/api/profile/get_profile/${encodeURIComponent(username)}`, options),

  myProfilePic: (options = {}) =>
    fetchWithAuth(`${BASE}/api/profile/get_profile_pic/me`, options),

  userProfilePic: (username, options = {}) =>
    fetchWithAuth(`${BASE}/api/profile/get_profile_pic/${encodeURIComponent(username)}`, options),

  userImages: (username, options = {}) =>
    fetchWithAuth(`${BASE}/api/profile/get_images/${encodeURIComponent(username)}`, options),

  myVisitors: (options = {}) =>
    fetchWithAuth(`${BASE}/api/profile/get_profile_visitors`, options),

  setLocation: (lat, lng, acc) =>
    fetchWithAuth(`${BASE}/api/profile/set_location`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ latitude: lat, longitude: lng, accuracy: acc }),
    }),

  /* -------- Interactions (object style) -------- */
  likeDislike: (likedUsername, options = {}) =>
    fetchWithAuth(`${BASE}/api/interactions/like_dislike`, {
      ...options,
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ liked_user: likedUsername }),
    }),

  getUsers: (type /* 'liked' | 'likers' */, options = {}) =>
    fetchWithAuth(`${BASE}/api/interactions/get_users/${encodeURIComponent(type)}`, options),

  isMatched: (otherUsername, options = {}) =>
    fetchWithAuth(`${BASE}/api/interactions/is_matched`, {
      ...options,
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ other_user: otherUsername }),
    }),

  block: (username, options = {}) =>
    fetchWithAuth(`${BASE}/api/interactions/block`, {
      ...options,
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ blocked_user: username }),
    }),

  unblock: (username, options = {}) =>
    fetchWithAuth(`${BASE}/api/interactions/unblock`, {
      ...options,
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ unblocked_user: username }),
    }),

  report: (username, options = {}) =>
    fetchWithAuth(`${BASE}/api/interactions/report`, {
      ...options,
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reported_user: username, reason: options.reason }),
    }),

  checkBlockStatus: (username, options = {}) =>
    fetchWithAuth(`${BASE}/api/interactions/check_block_status/${encodeURIComponent(username)}`, options),
};

/* =========================
 *  Tags / Interests helpers
 * ========================= */

export function addTags(tags = []) {
  return fetchWithAuth(`${BASE}/api/profile/add_tags`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tags }),
  });
}

export function deleteTag(tag) {
  return fetchWithAuth(`${BASE}/api/profile/delete_tag`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tag }),
  });
}

/* =========================
 *  Interactions (function style)
 *  (Both styles exported for compatibility)
 * ========================= */

export function likeOrDislike(username) {
  return fetchWithAuth(`${BASE}/api/interactions/like_dislike`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ liked_user: username }),
  });
}

// Optional explicit endpoints (only use if your backend exposes them)
export function likeUser(username) {
  return fetchWithAuth(`${BASE}/api/interactions/like`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ liked_user: username }),
  });
}

export function unlikeUser(username) {
  return fetchWithAuth(`${BASE}/api/interactions/unlike`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ liked_user: username }),
  });
}

export function blockUser(username) {
  return fetchWithAuth(`${BASE}/api/interactions/block`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ blocked_user: username }),
  });
}

export function unblockUser(username) {
  return fetchWithAuth(`${BASE}/api/interactions/unblock`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ unblocked_user: username }),
  });
}

export function reportUser(username, reason) {
  return fetchWithAuth(`${BASE}/api/interactions/report`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reported_user: username, reason }),
  });
}

export async function isMatched(username) {
  const res = await fetchWithAuth(`${BASE}/api/interactions/is_matched`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ other_user: username }),
  });
  return res.json();
}

export async function getLikedMe() {
  const res = await fetchWithAuth(`${BASE}/api/interactions/get_users/likers`);
  return res.json(); // { result: [...] }
}

export async function getILiked() {
  const res = await fetchWithAuth(`${BASE}/api/interactions/get_users/liked`);
  return res.json(); // { result: [...] }
}

/* =========================
 *  Profile pictures
 * ========================= */

export async function getAvatar(username) {
  const u = encodeURIComponent(username);
  const res = await fetchWithAuth(`${BASE}/api/profile/get_profile_pic/${u}`);
  return res.json(); // { status: "ok", result: "<url or null>" }
}
