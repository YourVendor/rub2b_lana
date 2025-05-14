import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import jwtDecode from "jwt-decode";

interface TokenPayload {
  role: string;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [role, setRole] = useState<string>("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      const decoded: TokenPayload = jwtDecode(token);
      setRole(decoded.role);
    }
  }, []);

  return (
    <div>
      <h1>Дашборд</h1>
      <button onClick={() => navigate("/admin")}>Админ</button>
      <button onClick={() => navigate("/moderator")}>Модератор</button>
      <button onClick={() => navigate("/goods")}>Товары</button>
      {(role === "moderator" || role === "admin") && (
        <button onClick={() => navigate("/moderator-item-to-goods")}>
          Сравнение позиций с витриной
        </button>
      )}
      {(role === "moderator" || role === "admin") && (
        <button onClick={() => navigate("/search_wb")}>
          Поисковые запросы Wildberries
        </button>
      )}
      {(role === "moderator" || role === "admin") && (
        <button onClick={() => navigate("/categories_search_words")}>
          Категории и ключевые слова
        </button>
      )}
    </div>
  );
};

export default Dashboard;