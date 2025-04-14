// frontend/src/components/Dashboard.tsx
import React from "react";
import { useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode"; // Исправлено

interface JwtPayload {
  sub: string;
  role: string;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const decoded: JwtPayload = token ? jwtDecode<JwtPayload>(token) : { sub: "", role: "" };

  return (
    <div>
      <h1>Дашборд</h1>
      <button onClick={() => navigate("/goods")}>Товары</button>
      {decoded.role === "admin" && (
        <button onClick={() => navigate("/admin")}>Админка</button>
      )}
      <div>Аналитика (скоро)</div>
    </div>
  );
};

export default Dashboard;