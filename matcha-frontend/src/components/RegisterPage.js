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
      <div className="form-wrapper">
        <h1>Create your account</h1>

        <form className="register-form" onSubmit={handleSubmit} noValidate>
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
            autoComplete="email"
          />

          <input
            type="text"
            name="username"
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
            required
            autoComplete="username"
          />

          <div className="name-fields">
            <input
              type="text"
              name="first_name"
              placeholder="First name"
              value={formData.first_name}
              onChange={handleChange}
              required
              autoComplete="given-name"
            />
            <input
              type="text"
              name="last_name"
              placeholder="Last name"
              value={formData.last_name}
              onChange={handleChange}
              required
              autoComplete="family-name"
            />
          </div>

          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
            autoComplete="new-password"
          />

          <button
            type="submit"
            className="register-btn"
            disabled={submitting}
          >
            {submitting ? "Registering…" : "Register"}
          </button>
        </form>

        {status && <p className="status">{status}</p>}
      </div>
    </div>
  );
};

export default RegisterPage;
