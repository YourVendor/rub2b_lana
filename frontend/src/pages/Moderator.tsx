import React, { useState, useEffect, useCallback } from "react";
import * as Papa from "papaparse";
import { CompanyItem, Company, Config } from "../types";

// Интерфейсы для внутренних типов
interface PreviewItem {
  [key: string]: string | number | null;
}

interface Unit {
  id: number;
  name: string;
}

interface DuplicateItem {
  identifier: string;
  name: string;
  brand: string | null;
  rrprice: number;
  microwholeprice: number;
  mediumwholeprice: number;
  maxwholeprice: number;
  stock: number;
  selected?: boolean;
}

interface NewItem {
  identifier: string;
  name: string;
  ean13: string | null;
  unit: string;
  brand: string | null;
  rrprice: number;
  microwholeprice: number;
  mediumwholeprice: number;
  maxwholeprice: number;
  stock: number;
}

interface ZeroPriceRow {
  identifier: string;
  name: string;
  brand: string | null;
  rrprice: number | null;
  microwholeprice: number | null;
  mediumwholeprice: number | null;
  maxwholeprice: number | null;
  zero_price_action?: string;
}

// Компонент для формы загрузки прайса
const PriceUploadForm: React.FC<{
  config: Config;
  setConfig: React.Dispatch<React.SetStateAction<Config>>;
  file: File | null;
  setFile: React.Dispatch<React.SetStateAction<File | null>>;
  companies: Company[];
  error: string | null;
  setError: React.Dispatch<React.SetStateAction<string | null>>;
  onPreview: () => void;
}> = ({ config, setConfig, file, setFile, companies, error, setError, onPreview }) => {
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  return (
    <div>
      <h2>Загрузка прайса</h2>
      <input type="file" accept=".xlsx,.xls" onChange={handleFileChange} />
      <div>
        <label>Компания для загрузки:</label>
        <select
          value={config.company_id}
          onChange={(e) => setConfig((prev) => ({ ...prev, company_id: parseInt(e.target.value) }))}
        >
          {companies.map((company) => (
            <option key={company.id} value={company.id}>
              {company.name} ({company.inn})
            </option>
          ))}
        </select>
      </div>
      <div>
        <label>Колонка идентификатора:</label>
        <input
          type="text"
          value={config.identifier_column}
          onChange={(e) => setConfig((prev) => ({ ...prev, identifier_column: e.target.value }))}
        />
      </div>
      <div>
        <label>Колонка EAN-13:</label>
        <input
          type="text"
          value={config.ean13_column}
          onChange={(e) => setConfig((prev) => ({ ...prev, ean13_column: e.target.value }))}
        />
      </div>
      <div>
        <label>Колонка наименования:</label>
        <input
          type="text"
          value={config.name_column}
          onChange={(e) => setConfig((prev) => ({ ...prev, name_column: e.target.value }))}
        />
      </div>
      <div>
        <label>Колонка единицы измерения:</label>
        <input
          type="text"
          value={config.unit_column}
          onChange={(e) => setConfig((prev) => ({ ...prev, unit_column: e.target.value }))}
        />
      </div>
      <div>
        <label>Колонка бренда:</label>
        <input
          type="text"
          value={config.brand_column}
          onChange={(e) => setConfig((prev) => ({ ...prev, brand_column: e.target.value }))}
          placeholder="Напр., Бренд"
        />
      </div>
      <div>
        <label>Колонка розничной цены:</label>
        <input
          type="text"
          value={config.rrprice_column}
          onChange={(e) => setConfig((prev) => ({ ...prev, rrprice_column: e.target.value }))}
          placeholder="Напр., Розничная цена"
        />
      </div>
      <div>
        <label>Колонка микрооптовой цены:</label>
        <input
          type="text"
          value={config.microwholeprice_column}
          onChange={(e) => setConfig((prev) => ({ ...prev, microwholeprice_column: e.target.value }))}
          placeholder="Напр., Микрооптовая цена"
        />
      </div>
      <div>
        <label>Колонка среднеоптовой цены:</label>
        <input
          type="text"
          value={config.mediumwholeprice_column}
          onChange={(e) => setConfig((prev) => ({ ...prev, mediumwholeprice_column: e.target.value }))}
          placeholder="Напр., Среднеоптовая цена"
        />
      </div>
      <div>
        <label>Колонка макрооптовой цены:</label>
        <input
          type="text"
          value={config.maxwholeprice_column}
          onChange={(e) => setConfig((prev) => ({ ...prev, maxwholeprice_column: e.target.value }))}
          placeholder="Напр., Макрооптовая цена"
        />
      </div>
      <div>
        <label>Колонка остатка:</label>
        <input
          type="text"
          value={config.stock_column}
          onChange={(e) => setConfig((prev) => ({ ...prev, stock_column: e.target.value }))}
        />
      </div>
      <div>
        <label>
          <input
            type="checkbox"
            checked={config.skip_first_row}
            onChange={(e) => setConfig((prev) => ({ ...prev, skip_first_row: e.target.checked }))}
          />
          Пропустить первую строку
        </label>
      </div>
      <div>
        <label>Обновление отсутствующих позиций:</label>
        <select
          value={config.update_missing}
          onChange={(e) => setConfig((prev) => ({ ...prev, update_missing: e.target.value }))}
        >
          <option value="zero">Обнулить остатки</option>
          <option value="null">Оставить пустым</option>
          <option value="ignore">Игнорировать</option>
        </select>
      </div>
      <div>
        <label>
          <input
            type="checkbox"
            checked={config.update_name}
            onChange={(e) => setConfig((prev) => ({ ...prev, update_name: e.target.checked }))}
          />
          Обновлять наименование
        </label>
      </div>
      <button onClick={onPreview}>Загрузить и показать превью</button>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
};

const Moderator: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<PreviewItem[]>([]);
  const [config, setConfig] = useState<Config>({
    company_id: 0,
    identifier_column: "",
    ean13_column: "",
    name_column: "",
    unit_column: "",
    brand_column: "",
    rrprice_column: "",
    microwholeprice_column: "",
    mediumwholeprice_column: "",
    maxwholeprice_column: "",
    stock_column: "",
    skip_first_row: true,
    update_missing: "ignore",
    update_name: false,
  });
  const [columns, setColumns] = useState<string[]>([]);
  const [items, setItems] = useState<CompanyItem[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [visibleColumns, setVisibleColumns] = useState({
    identifier: true,
    ean13: true,
    name: true,
    unit_id: true,
    brand: true,
    rrprice: true,
    microwholeprice: true,
    mediumwholeprice: true,
    maxwholeprice: true,
    stock: true,
  });
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [duplicates, setDuplicates] = useState<DuplicateItem[]>([]);
  const [unknownUnits, setUnknownUnits] = useState<string[]>([]);
  const [zeroPriceRows, setZeroPriceRow] = useState<ZeroPriceRow[]>([]);
  const [newItems, setNewItems] = useState<NewItem[]>([]);
  const [unitMappings, setUnitMappings] = useState<{ [key: string]: string }>({});
  const [ean13Decisions] = useState<{ [key: string]: string }>({});
  const [confirmedItems, setConfirmedItems] = useState<NewItem[]>([]);
  const [units, setUnits] = useState<Unit[]>([]);

  const loadItems = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (!token || !config.company_id) return;
    try {
      const response = await fetch(`http://127.0.0.1:8000/moderator/company-items/${config.company_id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Не удалось загрузить позиции");
      const data: CompanyItem[] = await response.json();
      setItems(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка");
    }
  }, [config.company_id]);

  const loadCompanies = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (!token) return;
    try {
      const response = await fetch("http://127.0.0.1:8000/moderator/companies", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Не удалось загрузить компании");
      const data: Company[] = await response.json();
      setCompanies(data);
      if (data.length > 0 && config.company_id === 0) {
        setConfig((prev) => ({ ...prev, company_id: data[0].id }));
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка");
    }
  }, [config.company_id, setConfig]);

  const loadUnits = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (!token) return;
    try {
      const response = await fetch("http://127.0.0.1:8000/units", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Не удалось загрузить единицы измерения");
      const data: Unit[] = await response.json();
      setUnits(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка");
    }
  }, []);

  useEffect(() => {
    loadCompanies();
    loadUnits();
  }, [loadCompanies, loadUnits]);

  useEffect(() => {
    if (config.company_id) {
      loadItems();
    }
  }, [config.company_id, loadItems]);

  const handlePreview = async () => {
    if (!file) {
      setError("Выберите файл");
      return;
    }
    if (
      !config.rrprice_column ||
      !config.microwholeprice_column ||
      !config.mediumwholeprice_column ||
      !config.maxwholeprice_column ||
      !config.identifier_column ||
      !config.name_column ||
      !config.unit_column ||
      !config.stock_column
    ) {
      setError("Заполните все обязательные поля");
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
      console.log("Preview data:", data);
      setPreview(data.preview || []);
      setColumns(data.columns || []);
      setDuplicates(data.duplicates || []);
      setUnknownUnits(data.unknown_units || []);
      setZeroPriceRow(data.zero_price_rows || []);
      setNewItems(data.new_items || []);
      setError(null);
      loadItems();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка");
    }
  };

  const handleConfirmUpload = async () => {
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
      const configData = {
        ...config,
        confirmed_items: confirmedItems,
        ean13_decisions: ean13Decisions,
        unit_mappings: unitMappings,
      };
      console.log("Config size:", JSON.stringify(configData).length);
      formData.append("config", JSON.stringify(configData));
      const response = await fetch("http://127.0.0.1:8000/moderator/confirm-upload", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Ошибка подтверждения");
      }
      const data = await response.json();
      setError(null);
      if (data.error_file) {
        window.location.href = `http://127.0.0.1:8000${data.error_file}`;
      }
      alert(
        `${data.message}\n` +
        `Обновлено: ${data.updated}, Добавлено: ${data.added}, Проигнорировано: ${data.ignored}\n` +
        `Обработано отсутствующих: ${data.missing_processed.length}`
      );
      loadItems();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка");
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
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка");
    }
  };

  const itemsPerPage = 50;
  const visibleItems = items.slice(0, page * itemsPerPage);
  const visiblePreview = preview.slice(0, 30);

  return (
    <div>
      <h1>Модератор</h1>
      <PriceUploadForm
        config={config}
        setConfig={setConfig}
        file={file}
        setFile={setFile}
        companies={companies}
        error={error}
        setError={setError}
        onPreview={handlePreview}
      />
      {duplicates.length > 0 && (
        <div>
          <h3>Дубликаты идентификаторов</h3>
          <table border={1}>
            <thead>
              <tr>
                <th>Идентификатор</th>
                <th>Наименование</th>
                <th>Бренд</th>
                <th>Розничная цена</th>
                <th>Микроопт</th>
                <th>Среднеопт</th>
                <th>Макроопт</th>
                <th>Остаток</th>
                <th>Выбрать</th>
              </tr>
            </thead>
            <tbody>
              {duplicates.map((dup, index) => (
                <tr key={index}>
                  <td>{dup.identifier}</td>
                  <td>{dup.name}</td>
                  <td>{dup.brand || "-"}</td>
                  <td>{dup.rrprice}</td>
                  <td>{dup.microwholeprice}</td>
                  <td>{dup.mediumwholeprice}</td>
                  <td>{dup.maxwholeprice}</td>
                  <td>{dup.stock}</td>
                  <td>
                    <input
                      type="radio"
                      name={`dup-${dup.identifier}`}
                      onChange={() => {
                        setDuplicates(duplicates.map((d, i) =>
                          d.identifier === dup.identifier ? { ...d, selected: i === index } : d
                        ));
                      }}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {unknownUnits.length > 0 && (
        <div>
          <h3>Неизвестные единицы измерения</h3>
          <table border={1}>
            <thead>
              <tr>
                <th>Единица</th>
                <th>Ассоциация</th>
              </tr>
            </thead>
            <tbody>
              {unknownUnits.map((unit, index) => (
                <tr key={index}>
                  <td>{unit}</td>
                  <td>
                    <select
                      value={unitMappings[unit] || ""}
                      onChange={(e) =>
                        setUnitMappings({ ...unitMappings, [unit]: e.target.value })
                      }
                    >
                      <option value="">Выберите...</option>
                      <option value="ignore">Игнорировать</option>
                      {units.map((u) => (
                        <option key={u.id} value={u.name}>
                          {u.name}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {zeroPriceRows.length > 0 && (
        <div>
          <h3>Пустые/нулевые цены</h3>
          <table border={1}>
            <thead>
              <tr>
                <th>Идентификатор</th>
                <th>Наименование</th>
                <th>Бренд</th>
                <th>Розничная цена</th>
                <th>Микроопт</th>
                <th>Среднеопт</th>
                <th>Макроопт</th>
                <th>Действие</th>
              </tr>
            </thead>
            <tbody>
              {zeroPriceRows.map((row, index) => (
                <tr key={index}>
                  <td>{row.identifier}</td>
                  <td>{row.name}</td>
                  <td>{row.brand || "-"}</td>
                  <td>{row.rrprice}</td>
                  <td>{row.microwholeprice}</td>
                  <td>{row.mediumwholeprice}</td>
                  <td>{row.maxwholeprice}</td>
                  <td>
                    <select
                      value={row.zero_price_action || "ignore"}
                      onChange={(e) => {
                        const newRows = [...zeroPriceRows];
                        newRows[index].zero_price_action = e.target.value;
                        setZeroPriceRow(newRows);
                      }}
                    >
                      <option value="ignore">Игнорировать</option>
                      <option value="error">Добавить в ошибки</option>
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {newItems.length > 0 && (
        <div>
          <h3>Новые позиции</h3>
          <input
            type="text"
            placeholder="Фильтр по наименованию"
            onChange={(e) => {
              setNewItems(newItems.filter((item) => item.name.includes(e.target.value)));
            }}
          />
          <table border={1}>
            <thead>
              <tr>
                <th>Идентификатор</th>
                <th>Наименование</th>
                <th>Бренд</th>
                <th>EAN-13</th>
                <th>Единица</th>
                <th>Розничная цена</th>
                <th>Микроопт</th>
                <th>Среднеопт</th>
                <th>Макроопт</th>
                <th>Остаток</th>
                <th>Подтвердить</th>
              </tr>
            </thead>
            <tbody>
              {newItems.slice(0, page * 100).map((item, index) => (
                <tr key={index}>
                  <td>{item.identifier}</td>
                  <td>{item.name}</td>
                  <td>{item.brand || "-"}</td>
                  <td>{item.ean13 || "-"}</td>
                  <td>{item.unit}</td>
                  <td>{item.rrprice}</td>
                  <td>{item.microwholeprice}</td>
                  <td>{item.mediumwholeprice}</td>
                  <td>{item.maxwholeprice}</td>
                  <td>{item.stock}</td>
                  <td>
                    <input
                      type="checkbox"
                      checked={confirmedItems.includes(item)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setConfirmedItems([...confirmedItems, item]);
                        } else {
                          setConfirmedItems(confirmedItems.filter((i) => i !== item));
                        }
                      }}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {newItems.length > page * 100 && (
            <button onClick={() => setPage(page + 1)}>Подгрузить ещё</button>
          )}
          <button
            onClick={() => {
              const csv = newItems.map((item) => ({
                identifier: item.identifier,
                name: item.name,
                brand: item.brand,
                ean13: item.ean13,
                unit: item.unit,
                rrprice: item.rrprice,
                microwholeprice: item.microwholeprice,
                mediumwholeprice: item.mediumwholeprice,
                maxwholeprice: item.maxwholeprice,
                stock: item.stock,
              }));
              const csvContent = Papa.unparse(csv);
              const blob = new Blob([csvContent], { type: "text/csv" });
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "new_items.csv";
              a.click();
              window.URL.revokeObjectURL(url);
            }}
          >
            Скачать неподтверждённые
          </button>
        </div>
      )}
      {preview.length > 0 && (
        <div>
          <h3>Превью (до 30 строк)</h3>
          <table border={1}>
            <thead>
              <tr>
                {columns.map((col) => (
                  <th key={col}>{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {visiblePreview.map((row, index) => (
                <tr key={index}>
                  {columns.map((col) => (
                    <td key={col}>{row[col] ?? "-"}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          <button onClick={handleConfirmUpload}>Применить экспорт</button>
        </div>
      )}
      <h2>Позиции компании</h2>
      <div>
        <label>Выберите компанию для отображения позиций:</label>
        <select
          value={config.company_id}
          onChange={(e) => setConfig((prev) => ({ ...prev, company_id: parseInt(e.target.value) }))}
        >
          {companies.map((company) => (
            <option key={company.id} value={company.id}>
              {company.name} ({company.inn})
            </option>
          ))}
        </select>
      </div>
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
            {visibleColumns.brand && <th>Бренд</th>}
            {visibleColumns.rrprice && <th>Розничная цена</th>}
            {visibleColumns.microwholeprice && <th>Микроопт</th>}
            {visibleColumns.mediumwholeprice && <th>Среднеопт</th>}
            {visibleColumns.maxwholeprice && <th>Макроопт</th>}
            {visibleColumns.stock && <th>Остаток</th>}
          </tr>
        </thead>
        <tbody>
          {visibleItems.map((item) => (
            <tr key={item.id}>
              {visibleColumns.identifier && <td>{item.identifier}</td>}
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
                  <select
                    value={item.unit_id || ""}
                    onChange={(e) =>
                      setItems(
                        items.map((i) =>
                          i.id === item.id
                            ? { ...i, unit_id: parseInt(e.target.value) || undefined }
                            : i
                        )
                      )
                    }
                  >
                    <option value="">-</option>
                    {units.map((unit) => (
                      <option key={unit.id} value={unit.id}>
                        {unit.name}
                      </option>
                    ))}
                  </select>
                </td>
              )}
              {visibleColumns.brand && (
                <td>
                  <input
                    value={item.brand || ""}
                    onChange={(e) =>
                      setItems(
                        items.map((i) =>
                          i.id === item.id ? { ...i, brand: e.target.value || null } : i
                        )
                      )
                    }
                  />
                </td>
              )}
              {visibleColumns.rrprice && (
                <td>
                  <input
                    type="number"
                    value={item.rrprice}
                    onChange={(e) =>
                      setItems(
                        items.map((i) =>
                          i.id === item.id ? { ...i, rrprice: parseFloat(e.target.value) } : i
                        )
                      )
                    }
                  />
                </td>
              )}
              {visibleColumns.microwholeprice && (
                <td>
                  <input
                    type="number"
                    value={item.microwholeprice}
                    onChange={(e) =>
                      setItems(
                        items.map((i) =>
                          i.id === item.id ? { ...i, microwholeprice: parseFloat(e.target.value) } : i
                        )
                      )
                    }
                  />
                </td>
              )}
              {visibleColumns.mediumwholeprice && (
                <td>
                  <input
                    type="number"
                    value={item.mediumwholeprice}
                    onChange={(e) =>
                      setItems(
                        items.map((i) =>
                          i.id === item.id ? { ...i, mediumwholeprice: parseFloat(e.target.value) } : i
                        )
                      )
                    }
                  />
                </td>
              )}
              {visibleColumns.maxwholeprice && (
                <td>
                  <input
                    type="number"
                    value={item.maxwholeprice}
                    onChange={(e) =>
                      setItems(
                        items.map((i) =>
                          i.id === item.id ? { ...i, maxwholeprice: parseFloat(e.target.value) } : i
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