import { BrowserRouter as Router, Routes, Route, useLocation } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Upload from "./pages/Upload";
import DisplayResponse from "./pages/DisplayResponse";
import Error from "./pages/Error";
import Logout from "./pages/Logout";
import Navbar from "./components/Navbar";
import './App.css';

function App() {
  return (
    <Router>
      <MainLayout />
    </Router>
  );
}

function MainLayout() {
  const location = useLocation();

  // Hide Navbar on login and logout pages
  const hideNavbar = ["/login", "/logout"].includes(location.pathname);

  return (
    <div>
      {!hideNavbar && <Navbar />}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/response" element={<DisplayResponse />} />
        <Route path="/logout" element={<Logout />} />
        <Route path="*" element={<Error />} />
      </Routes>
    </div>
  );
}

export default App;
