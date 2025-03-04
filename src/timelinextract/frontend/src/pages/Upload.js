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

    try {
      const response = await axios.post("http://127.0.0.1:8000/srcExtractor/upload/", formData);
      localStorage.setItem("response", JSON.stringify(response.data));
      navigate("/response");
    } catch (error) {
      alert("Upload failed");
      setLoading(false);
    }
  };

  return (
    <div className="upload-page">
      {loading ? (
        <div className="loading-container">
          <h2 className="loading-title">Processing your file...</h2>
          <p className="loading-message">Please wait while we analyze your PDF.</p>
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
