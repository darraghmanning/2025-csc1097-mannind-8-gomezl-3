import { useEffect } from "react";
import { googleLogout } from "@react-oauth/google";
import { useNavigate } from "react-router-dom";

function Logout({ onLogout }) {
  const navigate = useNavigate();

  useEffect(() => {
    // Perform logout when the component mounts
    googleLogout();
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    onLogout(); // Clear user state

    // Redirect to login page after logout
    navigate("/login");
  }, [navigate, onLogout]);

  return null;
}

export default Logout;
