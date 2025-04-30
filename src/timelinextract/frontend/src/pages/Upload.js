import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./Upload.css";

function Upload() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleUpload = async () => {
    if (!file) return alert("Please select a PDF");

    setLoading(true);
    const formData = new FormData();
    formData.append("pdf_file", file);

    const user = JSON.parse(localStorage.getItem("user"));
    if (user) {
      formData.append("email", user.email);
    }

    try {
      const response = await axios.post("https://two025-csc1097-mannind-8-gomezl-3.onrender.com/srcExtractor/upload/", formData);
      localStorage.setItem("response", JSON.stringify(response.data));
      navigate("/response");
    } catch (error) {
      // Extract and display the error from the backend
      const errorMessage = error.response?.data?.error || "Upload failed. Please try again.";
      alert(errorMessage);
      setLoading(false);
    }
  };

  return (
    <div className="upload-page">
      {loading ? (
        <div className="loading-container">
          <h2 className="loading-title">Processing your file...</h2>
          <p className="loading-message">Please wait while we analyse your PDF.</p>
          <div className="spinner"></div>
        </div>
      ) : (
        <div className="upload-container">
            <h2 className="upload-title">Upload a protocol in PDF format</h2>
            <div className="upload-box">
                <label className="upload-label">
                    {file && <p className="text-label">{file.name}</p>}
                    {!file && <p className="text-label">Drag & drop a file to upload or <u>browse</u></p>}
                    <input type="file" className="hidden" onChange={(e) => setFile(e.target.files[0])} />
                </label>
            </div>
            <button onClick={handleUpload} className={`upload-button ${file ? "enabled" : "disabled"}`} disabled={!file}>Upload</button>
        </div>
      )}
    </div>
  );
}

export default Upload;
