import React, { useState, useEffect } from "react";

interface CompanyItem {
  id: number;
  company_id: number;
  identifier: string;
  ean13?: string;
  name: string;
  unit_id?: number;
  base_price: number;
  stock: number;
}

const Moderator: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<any[]>([]);
  const [config, setConfig] = useState({
    company_id: 1,
    identifier_column: "",
    ean13_column: "",
    name_column: "",
    unit_column: "",
    price_column: "",
    stock_column: "",
    skip_first_row: true,
    update_missing: "zero",
    update_name: false,
  });
  const [columns, setColumns] = useState<string[]>([]);
  const [items, setItems] = useState<CompanyItem[]>([]);
  const [visibleColumns, setVisibleColumns] = useState({
    identifier: true,
    ean13: true,
    name: true,
    unit_id: true,
    base_price: true,
    stock: true,
  });
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const itemsPerPage = 50;

  const loadItems = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Токен отсутствует");
      return;
    }
    try {
      const response = await fetch(`http://127.0.0.1:8000/moderator/company-items/${config.company_id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Не удалось загрузить позиции");
      const data = await response.json();
      setItems(data);
    } catch (err: any) {
      setError(err.message);
    }
  };

  useEffect(() => {
    loadItems();
  }, [config.company_id]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handlePreview = async () => {
    if (!file) {
      setError("Выберите файл");
      return;
    }
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Токен отсутствует");
      return;
    }
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("config", JSON.stringify(config));
      const response = await fetch("http://127.0.0.1:8000/moderator/upload-price", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Ошибка загрузки");
      }
      const data = await response.json();
      setPreview(data.preview);
      setColumns(Object.keys(data.preview[0]));
      setError(null);
      loadItems();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleUpdateItem = async (item: CompanyItem) => {
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Токен отсутствует");
      return;
    }
    try {
      const response = await fetch(`http://127.0.0.1:8000/moderator/company-item/${item.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(item),
      });
      if (!response.ok) throw new Error("Ошибка обновления");
      loadItems();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const visibleItems = items.slice(0, page * itemsPerPage);

  return (
    <div>
      <h1>Модератор</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <h2>Загрузка прайса</h2>
      <input type="file" accept=".xlsx,.xls" onChange={handleFileChange} />
      <div>
        <label>Компания ID:</label>
        <input
          type="number"
          value={config.company_id}
          onChange={(e) => setConfig({ ...config, company_id: parseInt(e.target.value) })}
        />
      </div>
      <div>
        <label>Колонка идентификатора:</label>
        <input
          type="text"
          value={config.identifier_column}
          onChange={(e) => setConfig({ ...config, identifier_column: e.target.value })}
        />
      </div>
      <div>
        <label>Колонка EAN-13:</label>
        <input
          type="text"
          value={config.ean13_column}
          onChange={(e) => setConfig({ ...config, ean13_column: e.target.value })}
        />
      </div>
      <div>
        <label>Колонка наименования:</label>
        <input
          type="text"
          value={config.name_column}
          onChange={(e) => setConfig({ ...config, name_column: e.target.value })}
        />
      </div>
      <div>
        <label>Колонка единицы измерения:</label>
        <input
          type="text"
          value={config.unit_column}
          onChange={(e) => setConfig({ ...config, unit_column: e.target.value })}
        />
      </div>
      <div>
        <label>Колонка цены:</label>
        <input
          type="text"
          value={config.price_column}
          onChange={(e) => setConfig({ ...config, price_column: e.target.value })}
        />
      </div>
      <div>
        <label>Колонка остатка:</label>
        <input
          type="text"
          value={config.stock_column}
          onChange={(e) => setConfig({ ...config, stock_column: e.target.value })}
        />
      </div>
      <div>
        <label>
          <input
            type="checkbox"
            checked={config.skip_first_row}
            onChange={(e) => setConfig({ ...config, skip_first_row: e.target.checked })}
          />
          Пропустить первую строку
        </label>
      </div>
      <div>
        <label>Обновление отсутствующих позиций:</label>
        <select
          value={config.update_missing}
          onChange={(e) => setConfig({ ...config, update_missing: e.target.value })}
        >
          <option value="zero">Обнулить остатки</option>
          <option value="ignore">Игнорировать</option>
        </select>
      </div>
      <div>
        <label>
          <input
            type="checkbox"
            checked={config.update_name}
            onChange={(e) => setConfig({ ...config, update_name: e.target.checked })}
          />
          Обновлять наименование
        </label>
      </div>
      <button onClick={handlePreview}>Загрузить и показать превью</button>

      {preview.length > 0 && (
        <div>
          <h3>Превью (30 строк)</h3>
          <table border={1}>
            <thead>
              <tr>
                {columns.map((col) => (
                  <th key={col}>{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {preview.map((row, index) => (
                <tr key={index}>
                  {columns.map((col) => (
                    <td key={col}>{row[col]}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <h2>Позиции компании</h2>
      <div>
        <h3>Выберите колонки:</h3>
        {Object.keys(visibleColumns).map((col) => (
          <label key={col}>
            <input
              type="checkbox"
              checked={visibleColumns[col as keyof typeof visibleColumns]}
              onChange={(e) =>
                setVisibleColumns({ ...visibleColumns, [col]: e.target.checked })
              }
            />
            {col}
          </label>
        ))}
      </div>
      <table border={1}>
        <thead>
          <tr>
            {visibleColumns.identifier && <th>Идентификатор</th>}
            {visibleColumns.ean13 && <th>EAN-13</th>}
            {visibleColumns.name && <th>Наименование</th>}
            {visibleColumns.unit_id && <th>Единица</th>}
            {visibleColumns.base_price && <th>Цена</th>}
            {visibleColumns.stock && <th>Остаток</th>}
          </tr>
        </thead>
        <tbody>
          {visibleItems.map((item) => (
            <tr key={item.id}>
              {visibleColumns.identifier && (
                <td>{item.identifier}</td>
              )}
              {visibleColumns.ean13 && <td>{item.ean13 || "-"}</td>}
              {visibleColumns.name && (
                <td>
                  <input
                    value={item.name}
                    onChange={(e) =>
                      setItems(
                        items.map((i) =>
                          i.id === item.id ? { ...i, name: e.target.value } : i
                        )
                      )
                    }
                  />
                </td>
              )}
              {visibleColumns.unit_id && (
                <td>
                  <input
                    value={item.unit_id || ""}
                    onChange={(e) =>
                      setItems(
                        items.map((i) =>
                          i.id === item.id ? { ...i, unit_id: parseInt(e.target.value) || undefined } : i
                        )
                      )
                    }
                  />
                </td>
              )}
              {visibleColumns.base_price && (
                <td>
                  <input
                    type="number"
                    value={item.base_price}
                    onChange={(e) =>
                      setItems(
                        items.map((i) =>
                          i.id === item.id ? { ...i, base_price: parseFloat(e.target.value) } : i
                        )
                      )
                    }
                  />
                </td>
              )}
              {visibleColumns.stock && (
                <td>
                  <input
                    type="number"
                    value={item.stock}
                    onChange={(e) =>
                      setItems(
                        items.map((i) =>
                          i.id === item.id ? { ...i, stock: parseInt(e.target.value) } : i
                        )
                      )
                    }
                  />
                </td>
              )}
              <td>
                <button onClick={() => handleUpdateItem(item)}>Сохранить</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {items.length > visibleItems.length && (
        <button onClick={() => setPage(page + 1)}>Загрузить ещё</button>
      )}
    </div>
  );
};

export default Moderator;