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
import { useNavigate } from "react-router-dom";   // ✅ import navigate
import "./RegisterPage.css";

const RegisterPage = () => {
  const navigate = useNavigate();                // ✅ initialize navigate

  // State to hold form fields
  const [formData, setFormData] = useState({
    email: "",
    username: "",
    first_name: "",  // note the underscore
    last_name: "",
    password: ""
  });

  const [status, setStatus] = useState(null);

  // Update state when the user types in a field
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Send data to the back-end
  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://localhost:5000/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await response.json();
      console.log("9******************************", data);

      if (response.ok) {
        // ✅ show message, then auto-redirect after 2s
        setStatus("Check your email to verify your account.");
        setTimeout(() => navigate("/signin"), 2000);
      } else {
        setStatus(data.error || data.message);
      }
    } catch (error) {
      setStatus("Could not complete registration. Please try again.");
    }
  };

  return (
    <div className="register-container">
      <div className="form-wrapper">
        <h1>Create your account</h1>
        <form className="register-form" onSubmit={handleSubmit}>
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
          />
          <input
            type="text"
            name="username"
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
            required
          />
          <div className="name-fields">
            <input
              type="text"
              name="first_name"
              placeholder="First name"
              value={formData.first_name}
              onChange={handleChange}
              required
            />
            <input
              type="text"
              name="last_name"
              placeholder="Last name"
              value={formData.last_name}
              onChange={handleChange}
              required
            />
          </div>
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
          />

          <button type="submit" className="register-btn">
            Register
          </button>
        </form>

        {status && <p className="status">{status}</p>}
      </div>
    </div>
  );
};

export default RegisterPage;
