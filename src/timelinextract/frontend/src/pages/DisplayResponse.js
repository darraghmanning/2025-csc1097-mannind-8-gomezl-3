import { useEffect, useState } from "react";

function DisplayResponse() {
  const [response, setResponse] = useState(null);

  useEffect(() => {
    const storedResponse = localStorage.getItem("response");
    if (storedResponse) setResponse(JSON.parse(storedResponse));
  }, []);

  return (
    <div>
      <h2>Extracted Data</h2>
      {response ? <pre>{JSON.stringify(response, null, 2)}</pre> : <p>No data available.</p>}
    </div>
  );
}

export default DisplayResponse;
