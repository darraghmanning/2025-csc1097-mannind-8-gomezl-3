import { useEffect, useState } from "react";
import "./DisplayResponse.css";

function DisplayResponse() {
  const [response, setResponse] = useState(null);
  const [openCardIndex, setOpenCardIndex] = useState(null);

  useEffect(() => {
    const storedResponse = localStorage.getItem("response");
    if (storedResponse) setResponse(JSON.parse(storedResponse));
  }, []);

  const toggleCard = (index) => {
    setOpenCardIndex(openCardIndex === index ? null : index);
  };

  const renderTableRow = (label, value) => (
    <tr>
      <td className="label">{label}</td>
      <td className="value">{value || <span className="not-available">Not Available</span>}</td>
    </tr>
  );

  return (
    <div className="container">
      {response ? (
        <>
          <div className="overview-section">
            <h2>Extracted Study Overview</h2>
            <table className="overview-table">
              <tbody>
                {renderTableRow("Project Title", response["output"]["Project Title"])}
                {renderTableRow("Sponsor", response["output"]["Sponsor"])}
                {renderTableRow("Study Number", response["output"]["Study Number"])}
                {renderTableRow("Protocol Version and Date", response["output"]["Protocol Version and Date"])}
                {renderTableRow("Study Title", response["output"]["Study Title"])}
                {renderTableRow("Phase", response["output"]["Phase"])}
                {renderTableRow("Therapeutic Area", response["output"]["Therapeutic Area"])}
                {renderTableRow("Number of Patients", response["output"]["Number of Patients"])}
                {renderTableRow("Number of Sites", response["output"]["Number of Sites"])}
                {renderTableRow("Indication", response["output"]["Indication"])}
                {renderTableRow("Duration of Treatment", response["output"]["Duration of Treatment"])}
                {renderTableRow("Schedule of Assessments", response["output"]["Schedule of Assessments"])}
              </tbody>
            </table>
          </div>

          <div className="questionnaires-section">
            <h2>Questionnaires</h2>
            {response["output"]["questionnaires"]?.map((q, index) => (
              <div key={index} className="card">
                <button className="card-header" onClick={() => toggleCard(index)}>
                  <div>
                    <strong>{q.shortName}</strong> — {q.longName}
                    <span className="type-badge">{q.type}</span>
                  </div>
                  <span>{openCardIndex === index ? "▲" : "▼"}</span>
                </button>
                {openCardIndex === index && (
                  <div className="card-body">
                    <p><b>Timing:</b></p>
                    <ul>
                      {q.questionnaireTiming?.map((t, i) => <li key={i}>{t}</li>)}
                    </ul>
                    <p><b>Schedule extracted from text:</b> {q.questionnaireSchedule}</p> 
                  </div>
                )}
              </div>
            ))}
          </div>
        </>
      ) : (
        <p>No data available.</p>
      )}
    </div>
  );
}

export default DisplayResponse;
