// src/utils/api.js
export async function fetchWithAuth(url, options = {}) {
    const initialToken = localStorage.getItem("access_token");
    const baseHeaders = {
      "Content-Type": "application/json",
      ...(options.headers || {}),
      ...(initialToken ? { Authorization: `Bearer ${initialToken}` } : {}),
    };
  
    // First attempt
    let res = await fetch(url, {
      ...options,
      headers: baseHeaders,
      credentials: "include",
    });
  
    if (res.status !== 401 && res.status !== 403) return res;
  
    // Try refresh once
    const refreshRes = await fetch("http://localhost:5000/api/auth/refresh", {
      method: "GET",
      credentials: "include",
    });
    if (!refreshRes.ok) {
        // refresh failed → force sign-in
        window.location.href = "/dashboard";
        return res;
    }
    
    const { access_token } = await refreshRes.json();
    if (access_token) localStorage.setItem("access_token", access_token);
    
    const retryHeaders = {
        ...baseHeaders,
        Authorization: `Bearer ${access_token}`,
    };
    
    res = await fetch(url, {
        ...options,
        headers: retryHeaders,
        credentials: "include",
    });
    
    if (res.status === 401 || res.status === 403) {
        console.log("data = ", res)
        window.location.href = "/dashboard";
    }
    return res;
  }
  
  /* ---------- NEW: tag helpers ---------- */
  
  // Add multiple tags at once: body { "tags": ["hiking","cooking"] }
  export function addTags(tags = []) {
    return fetchWithAuth("http://localhost:5000/api/profile/add_tags", {
      method: "POST",
      body: JSON.stringify({ tags }),
    });
  }
  
  // Delete a single tag: body { "tag": "hiking" }
  export function deleteTag(tag) {
    return fetchWithAuth("http://localhost:5000/api/profile/delete_tag", {
      method: "POST",
      body: JSON.stringify({ tag }),
    });
  }

  