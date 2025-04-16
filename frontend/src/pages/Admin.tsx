import React, { useState, useEffect } from "react";

interface Query {
  id: number;
  name: string;
  query_text: string;
  author: string;
  active: boolean;
}

const Admin: React.FC = () => {
  const [structure, setStructure] = useState<string[]>([]);
  const [queryName, setQueryName] = useState("");
  const [queryText, setQueryText] = useState("");
  const [result, setResult] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [queries, setQueries] = useState<Query[]>([]);
  const [showDialog, setShowDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState<number | null>(null);
  const [overwriteQuery, setOverwriteQuery] = useState<Query | null>(null);

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

    const fetchQueries = async () => {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("Токен отсутствует, пожалуйста, войдите снова");
        return;
      }
      try {
        const response = await fetch("http://127.0.0.1:8000/admin/queries", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!response.ok) throw new Error("Не удалось загрузить запросы");
        const data = await response.json();
        setQueries(data);
      } catch (err: any) {
        setError(err.message);
      }
    };

    fetchStructure();
    fetchQueries();
  }, []);

  const handleQuery = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Токен отсутствует, пожалуйста, войдите снова");
      return;
    }
    if (!queryName) {
      setError("Введите имя запроса");
      return;
    }
    try {
      const response = await fetch("http://127.0.0.1:8000/admin/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: queryName,
          query_text: queryText,
          author: "germush",
          active: true,
        }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        if (errorData.detail.includes("Запрос с таким именем уже существует")) {
          const existing = queries.find((q) => q.name === queryName && q.author === "germush");
          setOverwriteQuery(existing || null);
          return;
        }
        throw new Error(errorData.detail || "Ошибка выполнения запроса");
      }
      const data = await response.json();
      setResult(data.result);
      setError(null);
      setQueryName("");
      setQueryText("");
      // Обновляем список запросов
      const queriesResponse = await fetch("http://127.0.0.1:8000/admin/queries", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (queriesResponse.ok) {
        setQueries(await queriesResponse.json());
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleOverwrite = async () => {
    const token = localStorage.getItem("token");
    if (!token || !overwriteQuery) return;
    try {
      const response = await fetch("http://127.0.0.1:8000/admin/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: queryName,
          query_text: queryText,
          author: "germush",
          active: true,
        }),
      });
      if (!response.ok) throw new Error("Ошибка перезаписи запроса");
      const data = await response.json();
      setResult(data.result);
      setError(null);
      setQueryName("");
      setQueryText("");
      setOverwriteQuery(null);
      // Обновляем список запросов
      const queriesResponse = await fetch("http://127.0.0.1:8000/admin/queries", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (queriesResponse.ok) {
        setQueries(await queriesResponse.json());
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleSelectQuery = (query: Query) => {
    setQueryName(query.name);
    setQueryText(query.query_text);
    setShowDialog(false);
  };

  const handleDeleteQuery = async (queryId: number) => {
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Токен отсутствует, пожалуйста, войдите снова");
      return;
    }
    try {
      const response = await fetch(`http://127.0.0.1:8000/admin/query/${queryId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Ошибка удаления запроса");
      setShowDeleteDialog(null);
      // Обновляем список запросов
      const queriesResponse = await fetch("http://127.0.0.1:8000/admin/queries", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (queriesResponse.ok) {
        setQueries(await queriesResponse.json());
      }
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
      <input
        type="text"
        value={queryName}
        onChange={(e) => setQueryName(e.target.value)}
        placeholder="Имя запроса"
      />
      <br />
      <textarea
        value={queryText}
        onChange={(e) => setQueryText(e.target.value)}
        rows={5}
        cols={50}
        placeholder="Введите SQL-запрос"
      />
      <br />
      <button onClick={handleQuery}>Выполнить</button>
      <button onClick={() => setShowDialog(true)}>Выбрать запрос</button>
      <pre>{JSON.stringify(result, null, 2)}</pre>

      {showDialog && (
        <div style={{ border: "1px solid black", padding: "10px", marginTop: "10px" }}>
          <h3>Активные запросы</h3>
          <ul>
            {queries.map((query) => (
              <li key={query.id}>
                {query.name} (автор: {query.author})
                <button onClick={() => handleSelectQuery(query)}>Выбрать</button>
                <button onClick={() => setShowDeleteDialog(query.id)}>Удалить</button>
              </li>
            ))}
          </ul>
          <button onClick={() => setShowDialog(false)}>Закрыть</button>
        </div>
      )}

      {overwriteQuery && (
        <div style={{ border: "1px solid black", padding: "10px", marginTop: "10px" }}>
          <p>Уверены ли вы в замене запроса "{overwriteQuery.name}"?</p>
          <button onClick={handleOverwrite}>Да</button>
          <button onClick={() => setOverwriteQuery(null)}>Нет</button>
        </div>
      )}

      {showDeleteDialog && (
        <div style={{ border: "1px solid black", padding: "10px", marginTop: "10px" }}>
          <p>Уверены ли вы в удалении запроса?</p>
          <button onClick={() => handleDeleteQuery(showDeleteDialog)}>Да</button>
          <button onClick={() => setShowDeleteDialog(null)}>Нет</button>
        </div>
      )}
    </div>
  );
};

export default Admin;