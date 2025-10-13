// Clear Profile Images - Browser Console Script
// Run this in your browser's console to clear the images from the mock profile

// Method 1: Clear localStorage (will require re-login)
localStorage.clear();
console.log("✅ Local storage cleared - please refresh and log in again");

// Method 2: Just clear the access token to force refresh
localStorage.removeItem("access_token");
console.log("✅ Access token cleared - page will reload profile data");

// Then refresh the page
window.location.reload();