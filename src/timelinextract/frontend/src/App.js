import React, { useState, useEffect } from "react";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Logout from "./pages/Logout";
import Upload from "./pages/Upload";
import DisplayResponse from "./pages/DisplayResponse";
import Error from "./pages/Error";
import Navbar from "./components/Navbar";

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;

function ProtectedRoute({ user, children }) {
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function MainLayout({ user, setUser }) {
  return (
    <div>
      {user && < Navbar />}
      <Routes>
        <Route path="/login" element={<Login onLoginSuccess={setUser} />} />
        <Route path="/" element={<ProtectedRoute user={user}><Home /></ProtectedRoute>} />
        <Route path="/upload" element={<ProtectedRoute user={user}><Upload /></ProtectedRoute>} />
        <Route path="/response" element={<ProtectedRoute user={user}><DisplayResponse /></ProtectedRoute>} />
        <Route path="/logout" element={<Logout onLogout={() => setUser(null)} />} />
        <Route path="*" element={<Error />} />
      </Routes>
    </div>
  );
}

function App() {
  const [user, setUser] = useState(null);

  // Load user from localStorage when the app starts
  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <Router>
        <MainLayout user={user} setUser={setUser} />
      </Router>
    </GoogleOAuthProvider>
  );
}

export default App;
