import { Link } from "react-router-dom";
import "./Home.css";

function Home() {
  return (
    <div className="home-container">
      <h1 class="home-title">Welcome to TimelineXtract System</h1>
      <p>
        Upload a clinical trial protocol in a PDF format for the extraction of information about the protocol.
      </p>
      <Link to="/upload">
        <img src="/arrow.png" alt="Arrow" className="arrow-image" />
      </Link>
    </div>
  );
}

export default Home;
