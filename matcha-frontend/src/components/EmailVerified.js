import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import "./EmailVerified.css";

/**
 * Email Verification Landing Page
 * Handles the redirect from email verification link
 * Stores tokens and redirects to appropriate page
 */
function EmailVerified() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [status, setStatus] = useState("verifying");
  const [message, setMessage] = useState("Verifying your email...");

  useEffect(() => {
    const processVerification = () => {
      // Get access token and redirect path from URL
      const accessToken = searchParams.get("access_token");
      const redirectPath = searchParams.get("redirect");
      const error = searchParams.get("error");

      // Handle errors
      if (error) {
        setStatus("error");
        switch (error) {
          case "invalid_token":
            setMessage("Invalid verification link. Please request a new verification email.");
            break;
          case "token_expired":
            setMessage("Verification link has expired. Please request a new verification email.");
            break;
          default:
            setMessage("Verification failed. Please try again or contact support.");
        }
        setTimeout(() => navigate("/"), 5000);
        return;
      }

      // Handle successful verification
      if (accessToken && redirectPath) {
        // Store access token in localStorage
        localStorage.setItem("access_token", accessToken);
        
        // Fetch user profile to get user details
        fetch("http://localhost:5000/api/profile/my_profile", {
          method: "GET",
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
          credentials: 'include',
        })
        .then(res => res.json())
        .then(userData => {
          // Set user in AuthContext to trigger socket connections
          login({
            id: userData.user_id,
            username: userData.username,
            email: userData.email,
            token: accessToken,
            ...userData
          });
        })
        .catch(err => {
          console.error("Failed to fetch user profile:", err);
          // Still log in with basic info if profile fetch fails
          login({ token: accessToken });
        });
        
        // Dispatch auth-changed event to update navbar
        window.dispatchEvent(new Event("auth-changed"));
        
        setStatus("success");
        setMessage("Email verified successfully! Redirecting...");
        
        // Redirect after 2 seconds
        setTimeout(() => {
          navigate(redirectPath, { replace: true });
        }, 2000);
      } else {
        setStatus("error");
        setMessage("Missing verification data. Please try again.");
        setTimeout(() => navigate("/"), 5000);
      }
    };

    processVerification();
  }, [searchParams, navigate, login]);

  return (
    <div className="email-verified-container">
      <div className="email-verified-card">
        {status === "verifying" && (
          <>
            <div className="spinner"></div>
            <h2>Verifying your email...</h2>
            <p>Please wait a moment.</p>
          </>
        )}

        {status === "success" && (
          <>
            <div className="success-icon">✓</div>
            <h2>Email Verified!</h2>
            <p>{message}</p>
            <div className="progress-bar">
              <div className="progress-fill"></div>
            </div>
          </>
        )}

        {status === "error" && (
          <>
            <div className="error-icon">✕</div>
            <h2>Verification Failed</h2>
            <p>{message}</p>
            <button onClick={() => navigate("/")}>Go to Home</button>
          </>
        )}
      </div>
    </div>
  );
}

export default EmailVerified;
