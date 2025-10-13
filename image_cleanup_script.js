/**
 * Image Cleanup Script for Browser Console
 * 
 * This script helps remove problematic images from the profile
 * Run this in your browser's developer console (F12 -> Console tab)
 */

console.log("🧹 Starting image cleanup...");

// Function to delete an image via API
async function deleteImageByPath(imagePath) {
    try {
        const token = localStorage.getItem("access_token");
        if (!token) {
            console.error("❌ No access token found. Please log in.");
            return false;
        }

        console.log(`🗑️ Attempting to delete: ${imagePath}`);
        
        const response = await fetch("http://localhost:5000/api/profile/delete_image", {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            credentials: "include",
            body: JSON.stringify({ image_path: imagePath })
        });

        const data = await response.json().catch(() => ({}));
        
        if (response.ok) {
            console.log(`✅ Successfully deleted: ${imagePath}`);
            return true;
        } else {
            console.error(`❌ Failed to delete ${imagePath}:`, data.error || response.status);
            return false;
        }
    } catch (error) {
        console.error(`❌ Error deleting ${imagePath}:`, error.message);
        return false;
    }
}

// Function to get current profile data
async function getCurrentProfile() {
    try {
        const token = localStorage.getItem("access_token");
        if (!token) {
            console.error("❌ No access token found");
            return null;
        }

        const response = await fetch("http://localhost:5000/api/profile/get_profile/me", {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            return data.result || data;
        } else {
            console.error("❌ Failed to fetch profile:", response.status);
            return null;
        }
    } catch (error) {
        console.error("❌ Error fetching profile:", error.message);
        return null;
    }
}

// Main cleanup function
async function cleanupImages() {
    console.log("📋 Getting current profile...");
    
    const profile = await getCurrentProfile();
    if (!profile) {
        console.error("❌ Could not fetch profile data");
        return;
    }

    const images = profile.images || [];
    console.log(`📸 Found ${images.length} images:`, images);

    if (images.length === 0) {
        console.log("✅ No images to clean up!");
        return;
    }

    // Delete each image
    for (let i = 0; i < images.length; i++) {
        const imagePath = images[i];
        console.log(`\n🔄 Processing image ${i + 1}/${images.length}`);
        await deleteImageByPath(imagePath);
        
        // Small delay between deletions
        await new Promise(resolve => setTimeout(resolve, 500));
    }

    console.log("\n🔄 Refreshing page to see changes...");
    setTimeout(() => window.location.reload(), 1000);
}

// Expose functions to global scope for manual use
window.deleteImageByPath = deleteImageByPath;
window.getCurrentProfile = getCurrentProfile;
window.cleanupImages = cleanupImages;

console.log(`
🎯 Image Cleanup Tools Ready!

Available commands:
• cleanupImages()           - Delete ALL images
• getCurrentProfile()       - View current profile data  
• deleteImageByPath(path)   - Delete specific image

To delete all images, run: cleanupImages()
`);