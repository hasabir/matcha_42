import React, { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

// Protected wrapper (keep yours)
import RequireAuth from "./routes/RequireAuth";

// Components (keep or adjust to your project)
import NavBar from "./components/Navbar";
import RegisterPage from "./components/RegisterPage";
import SignInPage from "./components/SignInPage";
import ProfileStepOne from "./components/ProfileStepOne";
import DiscoverPage from "./components/DiscoverPage";
import AccountSettingsPage from "./components/AccountSettingsPage";
import VerifyEmailPage from "./components/VerifyEmailPage";
import LandingPage from "./components/landingpage";

// Password reset flow
import ForgotPassword from "./components/ForgotPassword";
import ResetPassword from "./components/ressetpassword";
import ConfirmReset from "./components/ConfirmReset";

// User profile pages
import UserProfilePage from "./components/UserProfilePage";
import MyProfilePage from "./components/MyProfilePage";

// Auth validation
import { validateToken } from "./utils/authCheck";

function App() {
  const [authChecked, setAuthChecked] = useState(false);

  // Validate token on app startup
  useEffect(() => {
    const checkAuth = async () => {
      await validateToken();
      setAuthChecked(true);
    };
    checkAuth();

    // Load debug utilities in development
    if (process.env.NODE_ENV === 'development') {
      import('./utils/debugAuth').catch(err => console.log('Debug utilities not available:', err));
    }
  }, []);

  // Show nothing until we've checked auth status
  if (!authChecked) {
    return (
      <div style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        background: "linear-gradient(135deg, #fce7f3 0%, #f3e7fc 50%, #e7f0fc 100%)"
      }}>
        <div>Loading...</div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <NavBar />
      <Routes>
        {/* Public */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/signin" element={<SignInPage />} />
        <Route path="/verify/:token" element={<VerifyEmailPage />} />

        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/confirm-reset" element={<ConfirmReset />} />
        <Route path="/reset-password" element={<ResetPassword />} />

        {/* Private */}
        <Route element={<RequireAuth />}>
          <Route path="/profile-step-one" element={<ProfileStepOne />} />
          <Route path="/discover" element={<DiscoverPage />} />
          <Route path="/settings" element={<AccountSettingsPage />} />
          <Route path="/dashboard" element={<Navigate to="/profile" replace />} />
          <Route path="/profile" element={<MyProfilePage />} />
          <Route path="/profile/:username" element={<UserProfilePage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
