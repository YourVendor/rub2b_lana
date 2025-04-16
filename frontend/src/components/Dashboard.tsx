import React from "react";
import { useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";

interface TokenPayload {
  sub: string;
  role: string;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  let role = "";
  if (token) {
    const decoded: TokenPayload = jwtDecode(token);
    role = decoded.role;
  }

  return (
    <div>
      <h1>Дашборд</h1>
      <button onClick={() => navigate("/goods")}>Товары</button>
      {role === "admin" && <button onClick={() => navigate("/admin")}>Админка</button>}
      {(role === "admin" || role === "moderator") && (
        <button onClick={() => navigate("/moderator")}>Модератор</button>
      )}
    </div>
  );
};

export default Dashboard;