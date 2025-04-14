// frontend/src/pages/Admin.tsx
import React, { useState, useEffect } from "react";

const Admin: React.FC = () => {
  const [structure, setStructure] = useState<string[]>([]);
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<any[]>([]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    fetch("http://127.0.0.1:8000/admin/structure", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => setStructure(data.tables));
  }, []);

  const handleQuery = async () => {
    const token = localStorage.getItem("token");
    try {
      const response = await fetch("http://127.0.0.1:8000/admin/query", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ query_text: query, author: "germush", active: true }),
      });
      const data = await response.json();
      setResult(data.result);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div>
      <h1>Админка</h1>
      <h2>Структура базы</h2>
      <ul>{structure.map((table) => <li key={table}>{table}</li>)}</ul>
      <h2>SQL-запросы</h2>
      <textarea value={query} onChange={(e) => setQuery(e.target.value)} />
      <button onClick={handleQuery}>Выполнить</button>
      <pre>{JSON.stringify(result, null, 2)}</pre>
    </div>
  );
};

export default Admin;