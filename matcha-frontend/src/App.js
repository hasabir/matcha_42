import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

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
import Dashboard from "./components/dashboard";

// Password reset flow
import ForgotPassword from "./components/ForgotPassword";
import ResetPassword from "./components/ressetpassword";
import ConfirmReset from "./components/ConfirmReset";

function App() {
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
          <Route path="/dashboard" element={<Dashboard />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
