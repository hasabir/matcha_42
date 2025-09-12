// src/components/VerifyEmailPage.js
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const VerifyEmailPage = () => {
  const { token } = useParams();        // token comes from the URL: /verify/:token
  const navigate = useNavigate();
  const [status, setStatus] = useState('Verifying…');

  useEffect(() => {
    async function verifyEmail() {
      try {
        // The backtick string ensures `${token}` is interpolated
        const res = await fetch(`/api/auth/confirm_email/${token}`);
        const data = await res.json();
        if (res.ok) {
          setStatus(data.message || 'Email verified successfully');
          // Optional: store the access token if you want auto‑login
          // localStorage.setItem('access_token', data.access_token);
          // Delay and then redirect to the sign-in page
          setTimeout(() => navigate('/signin'), 2000);
        } else {
          setStatus(data.error || data.message);
        }
      } catch {
        setStatus('An error occurred while verifying your email.');
      }
    }
    verifyEmail();
  }, [token, navigate]);
  return (
    <div className="verify-container">
      <h1>Email Verification</h1>
      <p>{status}</p>
      {/* Optionally provide a manual link to sign‑in */}
      {status === 'Email verified successfully' &&
        <p><a href="/signin">Go to sign in</a></p>}
    </div>
  );
};

export default VerifyEmailPage;
