// src/components/VerifyEmailPage.js
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './VerifyEmailPage.css';

const VerifyEmailPage = () => {
  const { token } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('verifying'); // verifying, success, error
  const [message, setMessage] = useState('');

  useEffect(() => {
    async function verifyEmail() {
      if (!token) {
        setStatus('error');
        setMessage('Invalid verification link. No token provided.');
        return;
      }

      try {
        const res = await fetch(`http://localhost:5000/api/auth/confirm_email/${token}`, {
          method: 'GET',
          credentials: 'include'
        });
        
        const data = await res.json();
        
        if (res.ok) {
          setStatus('success');
          setMessage(data.message || 'Email verified successfully!');
          
          // Store the access token for auto-login
          if (data.access_token) {
            localStorage.setItem('access_token', data.access_token);
            // Notify app that user is authenticated
            window.dispatchEvent(new Event("auth-changed"));
          }
          
          // Get the redirect path from backend response
          const redirectPath = data.redirect_to || '/profile-step-one';
          
          // Redirect to the appropriate page after 3 seconds
          setTimeout(() => {
            navigate(redirectPath);
          }, 3000);
        } else {
          setStatus('error');
          setMessage(data.error || data.message || 'Email verification failed');
        }
      } catch (error) {
        console.error('Verification error:', error);
        setStatus('error');
        setMessage('An error occurred while verifying your email. Please try again or contact support.');
      }
    }
    
    verifyEmail();
  }, [token, navigate]);

  return (
    <div className="verify-email-container">
      <div className="verify-email-card">
        {/* Verifying State */}
        {status === 'verifying' && (
          <>
            <div className="verify-icon-wrapper verifying">
              <div className="verify-spinner"></div>
            </div>
            <h1 className="verify-title">Verifying Your Email</h1>
            <p className="verify-message">Please wait while we verify your email address...</p>
          </>
        )}

        {/* Success State */}
        {status === 'success' && (
          <>
            <div className="verify-icon-wrapper success">
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2"
                className="verify-icon"
              >
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </div>
            <h1 className="verify-title success">Email Verified!</h1>
            <p className="verify-message">{message}</p>
            <p className="verify-submessage">Redirecting you to complete your profile...</p>
            <div className="verify-progress-bar">
              <div className="verify-progress-fill"></div>
            </div>
          </>
        )}

        {/* Error State */}
        {status === 'error' && (
          <>
            <div className="verify-icon-wrapper error">
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2"
                className="verify-icon"
              >
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
              </svg>
            </div>
            <h1 className="verify-title error">Verification Failed</h1>
            <p className="verify-message">{message}</p>
            <div className="verify-actions">
              <button 
                className="verify-btn primary"
                onClick={() => navigate('/signin')}
              >
                Go to Sign In
              </button>
              <button 
                className="verify-btn secondary"
                onClick={() => navigate('/register')}
              >
                Create New Account
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default VerifyEmailPage;
