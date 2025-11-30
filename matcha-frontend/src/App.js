import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { AuthProvider } from './contexts/AuthContext';
import { NotificationProvider } from './contexts/NotificationContext';

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
import EmailVerified from "./components/EmailVerified";
import LandingPage from "./components/landingpage";

// Password reset flow
import ForgotPassword from "./components/ForgotPassword";
import ResetPassword from "./components/ressetpassword";
import ConfirmReset from "./components/ConfirmReset";

// User profile pages
import UserProfileView from "./components/UserProfileView";
// Chat interface for messaging matched users
import Chat from "./components/Chat";
import MyProfilePage from "./components/MyProfilePage";
import Notifications from "./components/Notifications";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <NotificationProvider>
          {/* <div className="app-wrapper" style={{ width: '100%', minHeight: '100vh' }}> */}
            <div 
              className="app-wrapper" 
              style={{ 
                width: '100%',
                minHeight: '100vh',
                display: 'flex',
                flexDirection: 'column'
              }}
            >
            <ToastContainer 
              position="top-right"
              autoClose={5000}
              hideProgressBar={false}
              newestOnTop
              closeOnClick
              rtl={false}
              pauseOnFocusLoss
              draggable
              pauseOnHover
              theme="light"
            />
            <NavBar />
            <main style={{ width: '100%', flex: 1 }}>
              <Routes>
            {/* Public */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/signin" element={<SignInPage />} />
            <Route path="/verify/:token" element={<VerifyEmailPage />} />
            <Route path="/email-verified" element={<EmailVerified />} />

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
              <Route path="/profile/:username" element={<UserProfileView />} />
            <Route path="/notifications" element={<Notifications />} />
            {/* Chat route – only available to authenticated users */}
            <Route path="/chat" element={<Chat />} />
            </Route>
              </Routes>
            </main>
          </div>
        </NotificationProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;