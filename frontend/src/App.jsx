import { useEffect, useState } from "react";

function App() {
  const [message, setMessage] = useState("Loading...");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/")
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch(() => setMessage("Could not reach the backend"));
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100">
      <h1 className="text-3xl font-bold text-slate-800">{message}</h1>
    </div>
  );
}

export default App;