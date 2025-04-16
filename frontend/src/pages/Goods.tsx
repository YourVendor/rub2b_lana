// frontend/src/pages/Goods.tsx
import React, { useState, useEffect } from "react";

interface GoodsItem {
  id: number;
  name: string;
  price: number;
  description?: string;
  category?: string;
  stock: number;
}

const Goods: React.FC = () => {
  const [goods, setGoods] = useState<GoodsItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchGoods = async () => {
      const token = localStorage.getItem("token");
      try {
        const response = await fetch("http://127.0.0.1:8000/goods", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!response.ok) throw new Error("Не удалось загрузить товары");
        const data = await response.json();
        setGoods(data);
        setError(null);
      } catch (err: any) {
        setError(err.message);
      }
    };
    fetchGoods();
  }, []);

  return (
    <div>
      <h1>Товары</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <table border={1}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Название</th>
            <th>Цена</th>
            <th>Описание</th>
            <th>Категория</th>
            <th>Остаток</th>
          </tr>
        </thead>
        <tbody>
          {goods.map((item) => (
            <tr key={item.id}>
              <td>{item.id}</td>
              <td>{item.name}</td>
              <td>{item.price}</td>
              <td>{item.description || "-"}</td>
              <td>{item.category || "-"}</td>
              <td>{item.stock}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Goods;