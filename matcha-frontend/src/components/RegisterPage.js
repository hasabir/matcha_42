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
import { validatePasswordStrength, getPasswordStrength } from "../utils/passwordValidator";
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

  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [status, setStatus] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState({ strength: 'none', color: '#ccc', message: '' });

  // Validation functions
  const validateEmail = (email) => {
    if (!email || !email.trim()) {
      return "Email is required";
    }
    
    // More strict email validation
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(email)) {
      return "Please enter a valid email address";
    }
    
    // Check for common typos in email
    const domain = email.split('@')[1];
    if (!domain) {
      return "Email must contain a valid domain";
    }
    
    // Check if domain has at least one dot and valid TLD
    if (!domain.includes('.')) {
      return "Email domain must have a valid extension (e.g., .com, .org)";
    }
    
    const domainParts = domain.split('.');
    const tld = domainParts[domainParts.length - 1];
    if (tld.length < 2) {
      return "Email domain extension is too short";
    }
    
    // Warn about obvious fake domains
    const fakeDomains = ['test.com', 'example.com', 'fake.com', 'asdf.com', 'qwerty.com'];
    if (fakeDomains.includes(domain.toLowerCase())) {
      return "Please use a real email address";
    }
    
    return null;
  };

  const validateUsername = (username) => {
    if (!username || !username.trim()) {
      return "Username is required";
    }
    if (username.length < 3) {
      return "Username must be at least 3 characters";
    }
    if (username.length > 20) {
      return "Username must be less than 20 characters";
    }
    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
      return "Username can only contain letters, numbers, and underscores";
    }
    return null;
  };

  const validateName = (name, fieldName) => {
    if (!name || !name.trim()) {
      return `${fieldName} is required`;
    }
    if (name.trim().length < 2) {
      return `${fieldName} must be at least 2 characters`;
    }
    if (name.trim().length > 50) {
      return `${fieldName} must be less than 50 characters`;
    }
    if (!/^[a-zA-Z\s'-]+$/.test(name)) {
      return `${fieldName} can only contain letters, spaces, hyphens, and apostrophes`;
    }
    return null;
  };

  const validateField = (name, value) => {
    switch (name) {
      case 'email':
        return validateEmail(value);
      case 'username':
        return validateUsername(value);
      case 'first_name':
        return validateName(value, 'First name');
      case 'last_name':
        return validateName(value, 'Last name');
      case 'password':
        const { isValid, error } = validatePasswordStrength(value, formData.username, formData.email);
        return isValid ? null : error;
      default:
        return null;
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((s) => ({ ...s, [name]: value }));
    
    // Validate field on change if it was already touched
    if (touched[name]) {
      const error = validateField(name, value);
      setErrors((prev) => ({ ...prev, [name]: error }));
    }
    
    // Update password strength indicator in real-time
    if (name === 'password') {
      const strength = getPasswordStrength(value);
      setPasswordStrength(strength);
    }
  };

  const handleBlur = (e) => {
    const { name, value } = e.target;
    setTouched((prev) => ({ ...prev, [name]: true }));
    
    // Validate field on blur
    const error = validateField(name, value);
    setErrors((prev) => ({ ...prev, [name]: error }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (submitting) return;

    setSubmitting(true);
    setStatus(null);

    // Mark all fields as touched
    setTouched({
      email: true,
      username: true,
      first_name: true,
      last_name: true,
      password: true
    });

    // Validate all fields
    const newErrors = {};
    Object.keys(formData).forEach((key) => {
      const error = validateField(key, formData[key]);
      if (error) {
        newErrors[key] = error;
      }
    });

    setErrors(newErrors);

    // Check if there are any validation errors
    if (Object.keys(newErrors).length > 0) {
      setStatus("Please fix the errors in the form");
      setSubmitting(false);
      return;
    }

    // Additional check: ensure no empty fields
    if (!formData.email.trim() || !formData.username.trim() || 
        !formData.first_name.trim() || !formData.last_name.trim() || 
        !formData.password) {
      setStatus("All fields are required");
      setSubmitting(false);
      return;
    }

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
        setStatus("✅ Check your email to verify your account.");
        setTimeout(() => navigate("/signin"), 2000);
      } else {
        // Error: show precise message, no redirect
        const errorMessage = data.error || data.message || "Registration failed.";
        
        // Handle specific error types and show in appropriate field
        if (errorMessage.toLowerCase().includes('email')) {
          if (errorMessage.includes('already exists')) {
            setErrors(prev => ({ ...prev, email: 'This email is already registered' }));
            setStatus("❌ " + errorMessage);
          } else if (errorMessage.includes('domain')) {
            setErrors(prev => ({ ...prev, email: errorMessage }));
            setStatus("❌ " + errorMessage);
          } else if (errorMessage.includes('format') || errorMessage.includes('invalid')) {
            setErrors(prev => ({ ...prev, email: errorMessage }));
            setStatus("❌ " + errorMessage);
          } else {
            setStatus("❌ " + errorMessage);
          }
        } else if (errorMessage.toLowerCase().includes('username')) {
          setErrors(prev => ({ ...prev, username: errorMessage }));
          setStatus("❌ " + errorMessage);
        } else if (errorMessage.toLowerCase().includes('password')) {
          setErrors(prev => ({ ...prev, password: errorMessage }));
          setStatus("❌ " + errorMessage);
        } else {
          setStatus("❌ " + errorMessage);
        }
      }
    } catch (err) {
      console.error("Registration error:", err);
      setStatus("❌ Could not complete registration. Please check your internet connection and try again.");
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
                <label className="form-label">Email Address *</label>
                <input
                  type="email"
                  name="email"
                  className={`form-input ${errors.email && touched.email ? 'input-error' : ''}`}
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  required
                  autoComplete="email"
                />
                {errors.email && touched.email && (
                  <span className="error-message">{errors.email}</span>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">Username *</label>
                <input
                  type="text"
                  name="username"
                  className={`form-input ${errors.username && touched.username ? 'input-error' : ''}`}
                  placeholder="Choose a username"
                  value={formData.username}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  required
                  autoComplete="username"
                />
                {errors.username && touched.username && (
                  <span className="error-message">{errors.username}</span>
                )}
                {!errors.username && touched.username && formData.username && (
                  <span className="form-hint">✓ Username is valid</span>
                )}
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">First Name *</label>
                  <input
                    type="text"
                    name="first_name"
                    className={`form-input ${errors.first_name && touched.first_name ? 'input-error' : ''}`}
                    placeholder="First name"
                    value={formData.first_name}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    required
                    autoComplete="given-name"
                  />
                  {errors.first_name && touched.first_name && (
                    <span className="error-message">{errors.first_name}</span>
                  )}
                </div>
                <div className="form-group">
                  <label className="form-label">Last Name *</label>
                  <input
                    type="text"
                    name="last_name"
                    className={`form-input ${errors.last_name && touched.last_name ? 'input-error' : ''}`}
                    placeholder="Last name"
                    value={formData.last_name}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    required
                    autoComplete="family-name"
                  />
                  {errors.last_name && touched.last_name && (
                    <span className="error-message">{errors.last_name}</span>
                  )}
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Password *</label>
                <input
                  type="password"
                  name="password"
                  className={`form-input ${errors.password && touched.password ? 'input-error' : ''}`}
                  placeholder="Create a strong password"
                  value={formData.password}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  required
                  autoComplete="new-password"
                />
                {errors.password && touched.password && (
                  <span className="error-message">{errors.password}</span>
                )}
                {formData.password && !errors.password && (
                  <div className="password-strength-indicator">
                    <div className="strength-bar-container">
                      <div 
                        className="strength-bar" 
                        style={{ 
                          width: passwordStrength.strength === 'strong' ? '100%' : 
                                 passwordStrength.strength === 'medium' ? '66%' : 
                                 passwordStrength.strength === 'weak' ? '33%' : '0%',
                          backgroundColor: passwordStrength.color
                        }}
                      />
                    </div>
                    <span className="strength-text" style={{ color: passwordStrength.color }}>
                      {passwordStrength.message}
                    </span>
                  </div>
                )}
                <span className="form-hint">
                  Must be at least 8 characters with uppercase, lowercase, numbers, and special characters. Avoid common words.
                </span>
              </div>

              <button
                type="submit"
                className="btn btn-primary btn-full btn-lg"
                disabled={submitting || Object.keys(errors).some(key => errors[key] !== null)}
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
              <div className={`status-message ${status.includes("✅") || status.toLowerCase().includes("check your email") ? "success" : "error"}`}>
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
