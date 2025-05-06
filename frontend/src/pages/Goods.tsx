import React, { useState, useEffect } from "react";
import { Goods as GoodsType, Price } from "../types";

const Goods: React.FC = () => {
  const [goods, setGoods] = useState<GoodsType[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchGoods = async () => {
      const token = localStorage.getItem("token");
      console.log("Token:", token);
      if (!token) {
        setError("Токен отсутствует");
        return;
      }
      try {
        const response = await fetch("http://127.0.0.1:8000/goods", {
          headers: { Authorization: `Bearer ${token}` },
        });
        console.log("Response status:", response.status, "OK:", response.ok);
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Не удалось загрузить товары: ${response.status} ${errorText}`);
        }
        const data = await response.json();
        console.log("fetchGoods: data", data);
        setGoods(data);
        setError(null);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Неизвестная ошибка");
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
            <th>EAN-13</th>
            <th>Название</th>
            <th>Цена (розн.)</th>
            <th>Описание</th>
            <th>Категория</th>
            <th>Остаток</th>
          </tr>
        </thead>
        <tbody>
          {goods.map((item) => {
            const rrprice = item.prices.find((p: Price) => p.price_type === "rrprice")?.price ?? "-";
            console.log(`Item ${item.ean13} prices:`, item.prices); // Отладка цен
            return (
              <tr key={item.ean13}>
                <td>{item.ean13}</td>
                <td>{item.name}</td>
                <td>{rrprice}</td>
                <td>{item.description || "-"}</td>
                <td>{item.category || "-"}</td>
                <td>{item.stock}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default Goods;