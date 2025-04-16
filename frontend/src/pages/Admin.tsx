// frontend/src/pages/Admin.tsx
import React, { useState, useEffect } from "react";

const Admin: React.FC = () => {
  const [structure, setStructure] = useState<string[]>([]);
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStructure = async () => {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("Токен отсутствует, пожалуйста, войдите снова");
        return;
      }
      try {
        const response = await fetch("http://127.0.0.1:8000/admin/structure", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!response.ok) throw new Error("Не удалось загрузить структуру");
        const data = await response.json();
        setStructure(data.tables);
        setError(null);
      } catch (err: any) {
        setError(err.message);
      }
    };
    fetchStructure();
  }, []);

  const handleQuery = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Токен отсутствует, пожалуйста, войдите снова");
      return;
    }
    try {
      const response = await fetch("http://127.0.0.1:8000/admin/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ query_text: query, author: "germush", active: true }),
      });
      if (!response.ok) throw new Error("Ошибка выполнения запроса");
      const data = await response.json();
      setResult(data.result);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div>
      <h1>Админка</h1>
      <h2>Структура базы</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <ul>
        {structure.map((table) => (
          <li key={table}>{table}</li>
        ))}
      </ul>
      <h2>SQL-запросы</h2>
      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        rows={5}
        cols={50}
      />
      <br />
      <button onClick={handleQuery}>Выполнить</button>
      <pre>{JSON.stringify(result, null, 2)}</pre>
    </div>
  );
};

export default Admin;