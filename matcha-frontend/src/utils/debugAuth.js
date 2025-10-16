// Debug utilities for authentication
// You can use these in the browser console

window.debugAuth = {
  // Check current auth state
  checkAuth: () => {
    const token = localStorage.getItem("access_token");
    console.log("Has token:", !!token);
    console.log("Token:", token ? token.substring(0, 20) + "..." : "null");
    return !!token;
  },
  
  // Clear all auth data
  clearAuth: () => {
    localStorage.removeItem("access_token");
    window.dispatchEvent(new Event("auth-changed"));
    console.log("Auth cleared. Page will update.");
  },
  
  // Set a test token
  setTestToken: () => {
    localStorage.setItem("access_token", "test_token_123");
    window.dispatchEvent(new Event("auth-changed"));
    console.log("Test token set. Page will update.");
  }
};

console.log("Debug auth utilities loaded. Use debugAuth.checkAuth(), debugAuth.clearAuth(), debugAuth.setTestToken()");