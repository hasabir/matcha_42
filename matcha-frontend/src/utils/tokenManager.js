// tokenManager.js
// Utility functions for managing authentication tokens

/**
 * Get the access token from localStorage
 * @returns {string|null} The access token or null if not found
 */
export const getToken = () => {
  return localStorage.getItem('access_token') || localStorage.getItem('token');
};

/**
 * Set the access token in localStorage
 * @param {string} token - The token to store
 */
export const setToken = (token) => {
  localStorage.setItem('access_token', token);
};

/**
 * Remove the access token from localStorage
 */
export const removeToken = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('token');
};

/**
 * Check if a token exists
 * @returns {boolean} True if token exists, false otherwise
 */
export const hasToken = () => {
  return Boolean(getToken());
};

/**
 * Decode JWT token payload (without verification)
 * @param {string} token - The JWT token
 * @returns {object|null} The decoded payload or null if invalid
 */
export const decodeToken = (token) => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Error decoding token:', error);
    return null;
  }
};

/**
 * Check if a token is expired
 * @param {string} token - The JWT token (optional, will use stored token if not provided)
 * @returns {boolean} True if expired, false otherwise
 */
export const isTokenExpired = (token) => {
  const tokenToCheck = token || getToken();
  if (!tokenToCheck) return true;

  const decoded = decodeToken(tokenToCheck);
  if (!decoded || !decoded.exp) return true;

  // Check if token is expired (exp is in seconds, Date.now() is in milliseconds)
  return decoded.exp * 1000 < Date.now();
};

/**
 * Get user ID from token
 * @returns {number|null} The user ID or null if not found
 */
export const getUserIdFromToken = () => {
  const token = getToken();
  if (!token) return null;

  const decoded = decodeToken(token);
  return decoded?.user_id || decoded?.sub || null;
};

/**
 * Get a valid token, refreshing if necessary
 * @returns {Promise<string|null>} The valid token or null if refresh fails
 */
export const getValidToken = async () => {
  const token = getToken();
  if (!token) {
    console.log('🔑 [TokenManager] No token found');
    return null;
  }

  // Check if token is expired
  if (isTokenExpired(token)) {
    console.log('🔑 [TokenManager] Token expired, attempting refresh...');
    try {
      const refreshResponse = await fetch('http://localhost:5000/api/auth/refresh', {
        method: 'POST',
        credentials: 'include', // Include cookies for refresh token
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (refreshResponse.ok) {
        const data = await refreshResponse.json();
        const newToken = data.access_token;
        setToken(newToken);
        console.log('✅ [TokenManager] Token refreshed successfully');
        return newToken;
      } else {
        console.error('❌ [TokenManager] Token refresh failed:', refreshResponse.status);
        removeToken();
        return null;
      }
    } catch (error) {
      console.error('❌ [TokenManager] Token refresh error:', error);
      removeToken();
      return null;
    }
  }

  console.log('✅ [TokenManager] Token is valid');
  return token;
};

/**
 * Make an authenticated fetch request with automatic token refresh
 * @param {string} url - The URL to fetch
 * @param {object} options - Fetch options
 * @returns {Promise<Response>} The fetch response
 */
export const authenticatedFetch = async (url, options = {}) => {
  const token = await getValidToken();
  if (!token) {
    throw new Error('No valid token available');
  }

  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
    ...options.headers,
  };

  return fetch(url, {
    ...options,
    headers,
  });
};

// Export as default object as well
export const tokenManager = {
  getToken,
  setToken,
  removeToken,
  hasToken,
  decodeToken,
  isTokenExpired,
  getUserIdFromToken,
  getValidToken,
  authenticatedFetch
};

export default tokenManager;
