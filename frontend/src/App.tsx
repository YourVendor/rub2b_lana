// frontend/src/App.tsx
import React, { useState } from "react";
import { Routes, Route, useNavigate } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import Admin from "./pages/Admin";
import Moderator from "./pages/Moderator";
import Goods from "./pages/Goods";
import ModeratorItemToGoods from "./pages/Moderator_item_to_goods";

const App: React.FC = () => {
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append("username", login);
      formData.append("password", password);

      const response = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Login failed");
      }

      const data = await response.json();
      localStorage.setItem("token", data.access_token);
      navigate("/dashboard");
    } catch (error: any) {
      console.error("Ошибка:", error);
      alert(error.message || "Неверный логин или пароль");
    }
  };

  return (
    <Routes>
      <Route
        path="/"
        element={
          <div>
            <h1>Вход</h1>
            <form onSubmit={handleSubmit}>
              <input
                type="text"
                value={login}
                onChange={(e) => setLogin(e.target.value)}
                placeholder="Логин"
              />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Пароль"
              />
              <button type="submit">Войти</button>
            </form>
          </div>
        }
      />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/admin" element={<Admin />} />
      <Route path="/moderator" element={<Moderator />} />
      <Route path="/goods" element={<Goods />} />
      <Route path="/moderator-item-to-goods" element={<ModeratorItemToGoods />} />
    </Routes>
  );
};

export default App;