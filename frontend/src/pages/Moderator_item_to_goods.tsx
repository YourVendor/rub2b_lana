// frontend/src/pages/Moderator_item_to_goods.tsx
import React, { useState, useEffect, useCallback } from "react";
import { CompanyItem, Company, Goods } from "../types";

const ModeratorItemToGoods: React.FC = () => {
  console.log("Rendering ModeratorItemToGoods"); // Добавлено
  const [companyId, setCompanyId] = useState<number>(0);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [items, setItems] = useState<CompanyItem[]>([]);
  const [goods, setGoods] = useState<Goods[]>([]);
  const [units, setUnits] = useState<{ id: number; name: string }[]>([]);
  const [ignoreItems, setIgnoreItems] = useState<Set<number>>(new Set());
  const [addNewItems, setAddNewItems] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);

  const loadCompanies = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Токен отсутствует");
      return;
    }
    try {
      const response = await fetch("http://127.0.0.1:8000/moderator/companies", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Не удалось загрузить компании");
      const data = await response.json();
      console.log("loadCompanies: data", data); // Добавлено
      setCompanies(data);
      if (data.length > 0 && companyId === 0) {
        setCompanyId(data[0].id);
      }
    } catch (err: any) {
      setError(err.message);
    }
  }, [companyId]);

  const loadItems = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (!token || !companyId) return;
    try {
      const response = await fetch(`http://127.0.0.1:8000/moderator/company-items/${companyId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Не удалось загрузить позиции");
      const data = await response.json();
      console.log("loadItems: data", data); // Добавлено
      setItems(data);
    } catch (err: any) {
      setError(err.message);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [companyId]);

  const loadGoods = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Токен отсутствует");
      return;
    }
    try {
      const response = await fetch("http://127.0.0.1:8000/goods", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Не удалось загрузить товары");
      const data = await response.json();
      console.log("loadGoods: data", data); // Добавлено
      setGoods(data);
    } catch (err: any) {
      setError(err.message);
    }
  }, []);

  const loadUnits = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Токен отсутствует");
      return;
    }
    try {
      const response = await fetch("http://127.0.0.1:8000/units", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Не удалось загрузить единицы измерения");
      const data = await response.json();
      console.log("loadUnits: data", data);
      setUnits(data);
    } catch (err: any) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    console.log("useEffect: companies", companies); // Добавлено
    console.log("useEffect: companyId", companyId); // Добавлено
    console.log("useEffect: items", items); // Добавлено
    console.log("useEffect: goods", goods); // Добавлено
    console.log("useEffect: units", units);
    console.log("useEffect: token", localStorage.getItem("token")); // Добавлено
    loadCompanies();
    loadGoods();
    loadUnits();
  }, [loadCompanies, loadGoods]);

  useEffect(() => {
    if (companyId) {
      loadItems();
    }
  }, [companyId, loadItems]);

  const handleUpdateMainCatalog = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Токен отсутствует");
      return;
    }
    try {
      const response = await fetch("http://127.0.0.1:8000/moderator/update-main-catalog", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          company_id: companyId,
          ignore_items: Array.from(ignoreItems),
          add_new_items: addNewItems,
          items: items.map((item) => ({
            id: item.id,
            ean13: item.ean13,
            name: item.name,
            unit_id: item.unit_id,
            rrprice: item.rrprice,
            microwholeprice: item.microwholeprice,
            mediumwholeprice: item.mediumwholeprice,
            maxwholeprice: item.maxwholeprice,
            stock: item.stock,
          })),
        }),
      });
      if (!response.ok) throw new Error("Ошибка обновления витрины");
      const data = await response.json();
      alert(`Обновлено: ${data.updated}, Добавлено: ${data.added}, Проигнорировано: ${data.ignored}`);
      loadGoods();
      loadItems();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const itemsPerPage = 50;
  const visibleItems = items.slice(0, page * itemsPerPage);

  return (
    <div>
      <h1>Сравнение позиций компании с витриной</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <div>
        <label>Компания:</label>
        <select
          value={companyId}
          onChange={(e) => setCompanyId(parseInt(e.target.value))}
        >
          {companies.map((company) => (
            <option key={company.id} value={company.id}>
              {company.name} ({company.inn})
            </option>
          ))}
        </select>
      </div>
      <div>
        <label>
          <input
            type="checkbox"
            checked={addNewItems}
            onChange={(e) => setAddNewItems(e.target.checked)}
          />
          Добавлять новые позиции
        </label>
      </div>
      <table border={1}>
        <thead>
          <tr>
            <th>Игнор</th>
            <th>Идентификатор</th>
            <th>EAN-13</th>
            <th>Наименование</th>
            <th>Единица</th>
            <th>Розн. цена</th>
            <th>Микроопт</th>
            <th>Среднеопт</th>
            <th>Макроопт</th>
            <th>Остаток</th>
            <th>Витрина: Наименование</th>
            <th>Витрина: Единица</th>
            <th>Витрина: Остаток</th>
          </tr>
        </thead>
        <tbody>
          {visibleItems.map((item) => {
            const good = goods.find((g) => g.ean13 === item.ean13);
            const isNew = !good;
            const unitDiff = good && item.unit_id !== good.unit_id;
            const nameDiff = good && item.name !== good.name;
            const stockDiff = good && item.stock !== good.stock;
            const unitName = units.find((u) => u.id === good?.unit_id)?.name || "-"; // Добавлено
            return (
              <tr key={item.id}>
                <td>
                  <input
                    type="checkbox"
                    checked={ignoreItems.has(item.id)}
                    onChange={(e) => {
                      const newIgnore = new Set(ignoreItems);
                      if (e.target.checked) {
                        newIgnore.add(item.id);
                      } else {
                        newIgnore.delete(item.id);
                      }
                      setIgnoreItems(newIgnore);
                    }}
                  />
                </td>
                <td>{item.identifier}</td>
                <td>{item.ean13 || "-"}</td>
                <td>{item.name}</td>
                <td style={{ backgroundColor: unitDiff ? "yellow" : "inherit" }}>
                  {units.find((u) => u.id === item.unit_id)?.name || item.unit_id || "-"}
                </td>
                <td>{item.rrprice}</td>
                <td>{item.microwholeprice}</td>
                <td>{item.mediumwholeprice}</td>
                <td>{item.maxwholeprice}</td>
                <td>{item.stock}</td>
                <td style={{ backgroundColor: nameDiff ? "lightblue" : "inherit" }}>
                  {isNew ? "новая" : good?.name}
                </td>
                <td style={{ backgroundColor: unitDiff ? "yellow" : "inherit" }}>
                  {isNew ? "новая" : unitName}
                </td>
                <td style={{ backgroundColor: stockDiff ? "lightblue" : "inherit" }}>
                  {isNew ? "новая" : good?.stock}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      {items.length > visibleItems.length && (
        <button onClick={() => setPage(page + 1)}>Подгрузить ещё</button>
      )}
      <button onClick={handleUpdateMainCatalog}>Обновить основную витрину</button>
    </div>
  );
};

export default ModeratorItemToGoods;