/**
 * Browser GPS Geolocation Utility
 * Handles requesting and obtaining user location from browser GPS
 */

/**
 * Request GPS location from browser
 * @returns {Promise<Object>} Location data with latitude, longitude, accuracy
 */
export const requestGPSLocation = () => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation is not supported by this browser'));
      return;
    }

    const options = {
      enableHighAccuracy: true,
      timeout: 10000, // 10 seconds
      maximumAge: 0 // Don't use cached position
    };

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy
        });
      },
      (error) => {
        let errorMessage = 'Failed to get location';
        
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = 'Location permission denied';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage = 'Location information unavailable';
            break;
          case error.TIMEOUT:
            errorMessage = 'Location request timed out';
            break;
          default:
            errorMessage = 'Unknown error occurred';
        }
        
        reject(new Error(errorMessage));
      },
      options
    );
  });
};

/**
 * Send location to backend API
 * @param {Object} location - Location object with latitude, longitude, etc.
 * @param {Function} fetchWithAuth - Authenticated fetch function
 * @returns {Promise<Object>} API response
 */
export const sendLocationToBackend = async (location, fetchWithAuth) => {
  try {
    const response = await fetchWithAuth('http://localhost:5000/api/profile/detect_location', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(location)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMsg = errorData.error || 'Failed to update location';
      console.warn('⚠️ Location update failed:', errorMsg);
      throw new Error(errorMsg);
    }

    return await response.json();
  } catch (error) {
    console.warn('⚠️ Error sending location to backend:', error.message);
    throw error;
  }
};

/**
 * Attempt to get and send GPS location, with IP fallback
 * @param {Function} fetchWithAuth - Authenticated fetch function
 * @returns {Promise<Object>} Result with location data
 */
export const detectAndSendLocation = async (fetchWithAuth) => {
  try {
    // Try GPS first
    console.log('🌍 Requesting GPS location...');
    const gpsLocation = await requestGPSLocation();
    console.log('✅ GPS location obtained:', gpsLocation);
    
    // Send GPS location to backend
    const result = await sendLocationToBackend(gpsLocation, fetchWithAuth);
    return {
      success: true,
      source: 'gps',
      ...result
    };
  } catch (gpsError) {
    console.warn('⚠️ GPS failed:', gpsError.message);
    console.log('🔄 Falling back to IP geolocation...');
    
    try {
      // Fallback to IP geolocation (backend will detect from request IP)
      const result = await sendLocationToBackend({}, fetchWithAuth);
      return {
        success: true,
        source: 'ip',
        ...result
      };
    } catch (ipError) {
      console.warn('⚠️ IP geolocation also failed:', ipError.message);
      // Don't throw - just return failure status for development environments
      return {
        success: false,
        error: 'Could not detect location',
        message: 'Location detection failed (this is normal in development)',
        isDevelopment: true
      };
    }
  }
};

/**
 * Check if location permission has been granted
 * @returns {Promise<string>} Permission state: 'granted', 'denied', or 'prompt'
 */
export const checkLocationPermission = async () => {
  if (!navigator.permissions) {
    return 'unknown';
  }

  try {
    const result = await navigator.permissions.query({ name: 'geolocation' });
    return result.state; // 'granted', 'denied', or 'prompt'
  } catch (error) {
    console.error('Error checking location permission:', error);
    return 'unknown';
  }
};
