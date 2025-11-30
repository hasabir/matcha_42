import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Restore user from token on app load
  useEffect(() => {
    const restoreUser = async () => {
      console.log('🔐 [AuthContext] Starting user restoration...');
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        console.log('⚠️ [AuthContext] No token found in localStorage');
        setIsLoading(false);
        return;
      }

      console.log('🔑 [AuthContext] Token found, validating...');

      try {
        const response = await fetch('http://localhost:5000/api/profile/my_profile', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          credentials: 'include',
        });

        if (response.ok) {
          const userData = await response.json();
          const userWithToken = {
            id: userData.user_id, // Backend returns 'user_id' not 'id'
            username: userData.username,
            email: userData.email,
            token: token, // Ensure token is always in user object
            ...userData
          };
          setUser(userWithToken);
          setIsAuthenticated(true);
          console.log('✅ [AuthContext] User restored successfully:', userData.username, '| ID:', userData.user_id);
          console.log('🔑 [AuthContext] Token attached to user object');
        } else {
          // Token is invalid - clear it
          console.warn('❌ [AuthContext] Token validation failed, clearing auth data');
          localStorage.removeItem('access_token');
          window.dispatchEvent(new Event('auth-changed'));
        }
      } catch (error) {
        console.error('❌ [AuthContext] Failed to restore user:', error);
        localStorage.removeItem('access_token');
        window.dispatchEvent(new Event('auth-changed'));
      } finally {
        setIsLoading(false);
        console.log('✅ [AuthContext] Auth initialization complete');
      }
    };

    restoreUser();
  }, []);

  const login = (userData) => {
    console.log('🔐 [AuthContext] Login initiated for:', userData.username || userData.id);
    
    // Ensure token is included in user object
    const token = userData.token || localStorage.getItem('access_token');
    const userWithToken = {
      ...userData,
      // Ensure id field is set correctly
      id: userData.id || userData.user_id,
      token: token
    };
    
    setUser(userWithToken);
    setIsAuthenticated(true);
    console.log('✅ [AuthContext] User logged in:', userData.username || userData.id);
    console.log('🔑 [AuthContext] Token status:', token ? 'Present' : 'Missing');
  };

  const logout = () => {
    console.log('🔐 [AuthContext] Logout initiated');
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('access_token');
    window.dispatchEvent(new Event('auth-changed'));
    console.log('✅ [AuthContext] User logged out successfully');
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    setUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
