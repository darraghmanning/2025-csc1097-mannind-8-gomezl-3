import { Link } from "react-router-dom";
import "./Navbar.css";

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="logo-container">
            <h1 className="logo">TimelineExtract</h1>
        </div>
        
        
        <ul className="nav-links">
          <li><Link to="/">Home</Link></li>
          <span className="separator">|</span>
          <li><Link to="/upload">Upload PDF</Link></li>
          <span className="separator">|</span>
          <li><Link to="/logout">Logout</Link></li>
        </ul>
      </div>
    </nav>
  );
}

export default Navbar;
