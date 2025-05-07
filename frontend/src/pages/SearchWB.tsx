import React, { useState, useEffect, useCallback } from "react";
import * as Papa from "papaparse";
import { SearchWBData, Category } from "../types";

interface AnalysisItem {
  query: string;
  is_new: boolean;
  avg_monthly: number | string;
  new_monthly: number;
}

const SearchWB: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [categoryIds, setCategoryIds] = useState<number[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [analysis, setAnalysis] = useState<AnalysisItem[]>([]);
  const [searchWb, setSearchWb] = useState<SearchWBData[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [fileId, setFileId] = useState<string | null>(null);
  const [errorFile, setErrorFile] = useState<string | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [updateProgress, setUpdateProgress] = useState<number>(0);

  const loadCategories = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (!token) return;
    try {
      const response = await fetch("http://127.0.0.1:8000/categories", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Не удалось загрузить категории");
      const data: Category[] = await response.json();
      setCategories(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка");
    }
  }, []);

  const loadSearchWb = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (!token) return;
    try {
      const response = await fetch("http://127.0.0.1:8000/search_wb", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Не удалось загрузить запросы");
      const data: SearchWBData[] = await response.json();
      setSearchWb(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка");
    }
  }, []);

  useEffect(() => {
    loadCategories();
    loadSearchWb();
  }, [loadCategories, loadSearchWb]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selected = Array.from(e.target.selectedOptions).map((option) =>
      parseInt(option.value)
    );
    setCategoryIds(selected);
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Выберите файл");
      return;
    }
    if (!categoryIds.length) {
      setError("Выберите хотя бы одну категорию");
      return;
    }
    
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Токен отсутствует");
      return;
    }
    
    setProgress(0);
    setError(null);
    setErrorFile(null);
    
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("category_ids", JSON.stringify(categoryIds));
      
      const response = await fetch("http://127.0.0.1:8000/search_wb/upload-csv", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Ошибка загрузки");
      }
      
      const data = await response.json();
      setAnalysis(data.analysis || []);
      setFileId(data.file_id);
      setErrorFile(data.error_file);
      
      // Мониторинг прогресса
      const interval = setInterval(async () => {
        const statusResponse = await fetch(
          `http://127.0.0.1:8000/search_wb/upload-status/${data.file_id}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        const statusData = await statusResponse.json();
        setProgress(statusData.progress);
        if (statusData.progress >= 100) {
          clearInterval(interval);
        }
      }, 1000);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка");
    }
  };

  const handleApplyUpdates = async () => {
    if (!fileId) {
      setError("Нет загруженного файла");
      return;
    }
    
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Токен отсутствует");
      return;
    }
    
    setUpdateProgress(0);
    setError(null);
    
    try {
      const response = await fetch("http://127.0.0.1:8000/search_wb/apply-updates", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ file_id: fileId }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Ошибка обновления");
      }
      
      const data = await response.json();
      alert(`Обновлено: ${data.updated}, Добавлено: ${data.added}`);
      setUpdateProgress(100);
      loadSearchWb();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка");
    }
  };

  return (
    <div>
      <h1>Поисковые запросы Wildberries</h1>
      <div>
        <h2>Загрузка CSV</h2>
        <div>
          <label>Выберите категории:</label>
          <select multiple value={categoryIds.map(String)} onChange={handleCategoryChange}>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
        </div>
        <input type="file" accept=".csv" onChange={handleFileChange} />
        <button onClick={handleUpload}>Загрузить и показать анализ</button>
        {progress > 0 && progress < 100 && (
          <div>
            <label>Прогресс загрузки: {Math.round(progress)}%</label>
            <progress value={progress} max="100" />
          </div>
        )}
        {error && <p style={{ color: "red" }}>{error}</p>}
        {errorFile && (
          <p>
            <a href={`http://127.0.0.1:8000${errorFile}`} download>
              Скачать файл ошибок
            </a>
          </p>
        )}
      </div>
      {analysis.length > 0 && (
        <div>
          <h3>Анализ запросов</h3>
          <table border={1}>
            <thead>
              <tr>
                <th>Запрос</th>
                <th>Новый</th>
                <th>Средний месячный</th>
                <th>Новый месячный</th>
              </tr>
            </thead>
            <tbody>
              {analysis.map((item, index) => (
                <tr key={index}>
                  <td>{item.query}</td>
                  <td>{item.is_new ? "Да" : "Нет"}</td>
                  <td>{item.avg_monthly}</td>
                  <td>{item.new_monthly}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <button onClick={handleApplyUpdates}>Применить обновление запросов</button>
          {updateProgress > 0 && updateProgress < 100 && (
            <div>
              <label>Прогресс обновления: {Math.round(updateProgress)}%</label>
              <progress value={updateProgress} max="100" />
            </div>
          )}
        </div>
      )}
      <h2>Список запросов</h2>
      <table border={1}>
        <thead>
          <tr>
            <th>Запрос</th>
            <th>Частота в месяц</th>
            <th>Категории</th>
            <th>Конкуренты</th>
          </tr>
        </thead>
        <tbody>
          {searchWb.map((item, index) => (
            <tr key={index}>
              <td>{item.text}</td>
              <td>{item.frequency_per_month}</td>
              <td>{item.categories}</td>
              <td>
                {item.competitors.map((comp, idx) => (
                  <span key={idx}>
                    <a href={comp.hyperlink} target="_blank" rel="noopener noreferrer">
                      {comp.name}
                    </a>
                    {idx < item.competitors.length - 1 ? ", " : ""}
                  </span>
                ))}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default SearchWB;