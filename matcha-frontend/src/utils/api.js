// src/utils/api.js

const BASE = "http://localhost:5000";

/**
 * fetchWithAuth
 * - Attaches Authorization: Bearer <access_token> if present
 * - On 401/403 tries a one-time refresh via POST /api/auth/refresh (cookie-based)
 * - Retries the original request with the new access token
 * - Redirects to /signin if refresh fails or retry is still unauthorized
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

  // If still unauthorized, force re-login
  if (res.status === 401 || res.status === 403) {
    window.location.href = "/signin";
  }

  return res;
}

/* =========================
 *  Profile / Location APIs
 * ========================= */

export const api = {
  meProfile: () =>
    fetchWithAuth(`${BASE}/api/profile/get_profile/me`),

  userProfile: (username) =>
    fetchWithAuth(`${BASE}/api/profile/get_profile/${encodeURIComponent(username)}`),

  myProfilePic: () =>
    fetchWithAuth(`${BASE}/api/profile/get_profile_pic/me`),

  userProfilePic: (username) =>
    fetchWithAuth(`${BASE}/api/profile/get_profile_pic/${encodeURIComponent(username)}`),

  userImages: (username) =>
    fetchWithAuth(`${BASE}/api/profile/get_images/${encodeURIComponent(username)}`),

  myVisitors: () =>
    fetchWithAuth(`${BASE}/api/profile/get_profile_vistors`),

  setLocation: (lat, lng, acc) =>
    fetchWithAuth(`${BASE}/api/profile/set_location`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ latitude: lat, longitude: lng, accuracy: acc }),
    }),

  /* -------- Interactions (object style) -------- */
  likeDislike: (likedUsername) =>
    fetchWithAuth(`${BASE}/api/interactions/like_dislike`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ liked_user: likedUsername }),
    }),

  getUsers: (type /* 'liked' | 'likers' */) =>
    fetchWithAuth(`${BASE}/api/interactions/get_users/${encodeURIComponent(type)}`),

  isMatched: (otherUsername) =>
    fetchWithAuth(`${BASE}/api/interactions/is_matched`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ other_user: otherUsername }),
    }),

  block: (username) =>
    fetchWithAuth(`${BASE}/api/interactions/block`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ blocked_user: username }),
    }),

  unblock: (username) =>
    fetchWithAuth(`${BASE}/api/interactions/unblock`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ unblocked_user: username }),
    }),

  report: (username, reason) =>
    fetchWithAuth(`${BASE}/api/interactions/report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reported_user: username, reason }),
    }),
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

/* =========================
 *  Chat / Messaging APIs
 * ========================= */

export const chatApi = {
  // Get all conversations for the current user
  getConversations: () =>
    fetchWithAuth(`${BASE}/api/chat/conversations`),

  // Get or create conversation with a specific user (and get messages)
  getConversation: (username) =>
    fetchWithAuth(`${BASE}/api/chat/conversation/${encodeURIComponent(username)}`),

  // Send a message to a specific user
  sendMessageToUser: (username, message) =>
    fetchWithAuth(`${BASE}/api/chat/conversation/${encodeURIComponent(username)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    }),

  // Send a message to a conversation by ID
  sendMessage: (conversationId, message) =>
    fetchWithAuth(`${BASE}/api/chat/send`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conversation_id: conversationId, message }),
    }),

  // Get messages from a conversation
  getMessages: (conversationId, limit = 100, offset = 0) =>
    fetchWithAuth(`${BASE}/api/chat/messages/${conversationId}?limit=${limit}&offset=${offset}`),

  // Mark conversation messages as read
  markAsRead: (conversationId) =>
    fetchWithAuth(`${BASE}/api/chat/mark_read/${conversationId}`, {
      method: "POST",
    }),

  // Get unread message count
  getUnreadCount: () =>
    fetchWithAuth(`${BASE}/api/chat/unread_count`),
};

// Export individual chat functions for convenience
export async function getConversations() {
  const res = await chatApi.getConversations();
  return res.json();
}

export async function getConversationWith(username) {
  const res = await chatApi.getConversation(username);
  return res.json();
}

export async function sendChatMessage(username, message) {
  const res = await chatApi.sendMessageToUser(username, message);
  return res.json();
}

export async function getUnreadMessageCount() {
  const res = await chatApi.getUnreadCount();
  return res.json();
}

/* =========================
 *  Notification APIs
 * ========================= */

export const notificationApi = {
  // Get notifications (with optional filters)
  getNotifications: (limit = 50, unreadOnly = false) =>
    fetchWithAuth(`${BASE}/api/notifications/get_notifications?limit=${limit}&unread_only=${unreadOnly}`),

  // Get unread notification count
  getUnreadCount: () =>
    fetchWithAuth(`${BASE}/api/notifications/unread_count`),

  // Mark a specific notification as read
  markAsRead: (notificationId) =>
    fetchWithAuth(`${BASE}/api/notifications/mark_read/${notificationId}`, {
      method: "POST",
    }),

  // Mark all notifications as read
  markAllAsRead: () =>
    fetchWithAuth(`${BASE}/api/notifications/mark_all_read`, {
      method: "POST",
    }),

  // Delete a notification
  deleteNotification: (notificationId) =>
    fetchWithAuth(`${BASE}/api/notifications/delete/${notificationId}`, {
      method: "DELETE",
    }),
};

