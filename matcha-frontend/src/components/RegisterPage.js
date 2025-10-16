// import React from "react";
// import "./RegisterPage.css";

// const RegisterPage = () => {
//   return (
//     <div className="register-container">
//       {/* The navigation bar is now handled globally in App.js via <NavBar /> */}

//       {/* Main registration section */}
//       <div className="form-wrapper">
//         <h1>Create your account</h1>
//         <form
//           className="register-form"
//           onSubmit={(e) => {
//             e.preventDefault();
//             // Handle form submission logic here
//             console.log("Form submitted");
//           }}
//         >
//           <input type="email" name="email" placeholder="Email" required />
//           <input type="text" name="username" placeholder="Username" required />
//           <div className="name-fields">
//             <input
//               type="text"
//               name="firstName"
//               placeholder="First name"
//               required
//             />
//             <input
//               type="text"
//               name="lastName"
//               placeholder="Last name"
//               required
//             />
//           </div>
//           <input type="password" name="password" placeholder="Password" required />
//           <button type="submit" className="register-btn">
//             Register
//           </button>
//         </form>
//         <p className="terms">
//           By registering, you agree to our Terms of Service and Privacy Policy.
//         </p>
//       </div>
//     </div>
//   );
// };

// export default RegisterPage;


import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./RegisterPage.css";

const RegisterPage = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    email: "",
    username: "",
    first_name: "",
    last_name: "",
    password: ""
  });

  const [status, setStatus] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e) => {
    setFormData((s) => ({ ...s, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (submitting) return;

    setSubmitting(true);
    setStatus(null);

    try {
      const payload = {
        email: formData.email.trim(),
        username: formData.username.trim(),
        first_name: formData.first_name.trim(),
        last_name: formData.last_name.trim(),
        password: formData.password
      };

      const response = await fetch("http://localhost:5000/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json().catch(() => ({}));

      if (response.ok) {
        // Success: show message then redirect to signin
        setStatus("Check your email to verify your account.");
        setTimeout(() => navigate("/signin"), 2000);
      } else {
        // Error: show precise message, no redirect
        setStatus(data.error || data.message || "Registration failed.");
      }
    } catch (err) {
      setStatus("Could not complete registration. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="register-container">
      <div className="register-content">
        {/* Left Side - Branding */}
        <div className="register-left">
          <div className="brand-content">
            <div className="brand-logo">
              <span className="logo-icon">💕</span>
              <h2 className="brand-name">MatchUp</h2>
            </div>
            <h1 className="brand-title">Start Your Love Journey</h1>
            <p className="brand-subtitle">
              Join thousands of people finding meaningful connections and lasting relationships.
            </p>
            <div className="brand-features">
              <div className="feature-item">
                <span className="feature-icon">✓</span>
                <span>Smart Matching Algorithm</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">✓</span>
                <span>Verified Profiles</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">✓</span>
                <span>Safe & Secure</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Form */}
        <div className="register-right">
          <div className="form-wrapper">
            <div className="form-header">
              <h1 className="form-title">Create Your Account</h1>
              <p className="form-subtitle">
                Already have an account?{" "}
                <button 
                  className="link-btn" 
                  onClick={() => navigate("/signin")}
                >
                  Sign In
                </button>
              </p>
            </div>

            <form className="register-form" onSubmit={handleSubmit} noValidate>
              <div className="form-group">
                <label className="form-label">Email Address</label>
                <input
                  type="email"
                  name="email"
                  className="form-input"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  autoComplete="email"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Username</label>
                <input
                  type="text"
                  name="username"
                  className="form-input"
                  placeholder="Choose a username"
                  value={formData.username}
                  onChange={handleChange}
                  required
                  autoComplete="username"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">First Name</label>
                  <input
                    type="text"
                    name="first_name"
                    className="form-input"
                    placeholder="First name"
                    value={formData.first_name}
                    onChange={handleChange}
                    required
                    autoComplete="given-name"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Last Name</label>
                  <input
                    type="text"
                    name="last_name"
                    className="form-input"
                    placeholder="Last name"
                    value={formData.last_name}
                    onChange={handleChange}
                    required
                    autoComplete="family-name"
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Password</label>
                <input
                  type="password"
                  name="password"
                  className="form-input"
                  placeholder="Create a strong password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  autoComplete="new-password"
                />
                <span className="form-hint">
                  Must be at least 8 characters
                </span>
              </div>

              <button
                type="submit"
                className="btn btn-primary btn-full btn-lg"
                disabled={submitting}
              >
                {submitting ? (
                  <>
                    <span className="spinner-sm"></span>
                    Creating Account...
                  </>
                ) : (
                  "Create Account"
                )}
              </button>
            </form>

            {status && (
              <div className={`status-message ${status.includes("email") ? "success" : "error"}`}>
                {status}
              </div>
            )}

            <p className="terms-text">
              By creating an account, you agree to our{" "}
              <a href="/terms" className="terms-link">Terms of Service</a>
              {" "}and{" "}
              <a href="/privacy" className="terms-link">Privacy Policy</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
