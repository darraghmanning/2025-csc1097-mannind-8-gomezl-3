import { GoogleLogin } from "@react-oauth/google";
import React, { useState } from "react";
import axios from "axios";
import { jwtDecode } from "jwt-decode";
import { useNavigate } from "react-router-dom";
import "./Login.css";

function Login({ onLoginSuccess }) {
    const navigate = useNavigate();
    const [error, setError] = useState(null);
  
    const handleSuccess = async (response) => {
      console.log("Google Login Success:", response);
      const { credential } = response;
      const decoded = jwtDecode(credential);
  
      try {
        // Send token to Django backend for verification
        const res = await axios.post("http://127.0.0.1:8000/srcExtractor/auth/google/", { token: credential });
  
        // Save token & user info
        localStorage.setItem("token", res.data.access);
        localStorage.setItem("user", JSON.stringify(decoded));
  
        onLoginSuccess(decoded);
        navigate("/");  // Redirect to Home page
      } catch (error) {
        // Safely extract backend error message if available
        const message = error.response?.data?.error || "Google authentication failed. Please try again.";
        setError(message);
        console.error("Google authentication failed:", error);
      }
    };
  
    const handleFailure = (error) => {
      setError("Google login failed. Please try again.");
      console.error("Google Login Failed:", error);
    };
  
    return (
      <div className="login-container">
        <h1 className="login-title">Sign in with your DCU account to access the TimelineXtract System.</h1>
        <GoogleLogin onSuccess={handleSuccess} onError={handleFailure} />
        {error && <p className="error">{error}</p>}
      </div>
    );
}

export default Login;
