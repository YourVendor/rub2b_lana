import React, { useState, useEffect, useCallback, useMemo, useRef } from "react";
import Select, { SingleValue } from "react-select";
import { Goods, Category, SearchWordsWB } from "../types";

interface CategoryGroup {
  id: number;
  name: string;
  search_words: SearchWordsWB[];
}

interface OptionType {
  value: number;
  label: string;
}

const CategoriesSearchWords: React.FC = () => {
  const [goods, setGoods] = useState<Goods[]>([]);
  const [displayedGoods, setDisplayedGoods] = useState<Goods[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [searchWords, setSearchWords] = useState<{ [key: string]: SearchWordsWB[] }>({});
  const [offset, setOffset] = useState(0);
  const [displayOffset, setDisplayOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [categoryGroups, setCategoryGroups] = useState<CategoryGroup[]>([]);
  const [newCategoryName, setNewCategoryName] = useState("");
  const [newSearchWord, setNewSearchWord] = useState<{ [key: string]: string }>({});
  const [loadedGoodsIds, setLoadedGoodsIds] = useState<Set<string>>(new Set());
  const [isLoadingGoods, setIsLoadingGoods] = useState(false);
  const [isLoadingCategories, setIsLoadingCategories] = useState(false);
  const [isLoadingCategoryGroups, setIsLoadingCategoryGroups] = useState(false);
  const [isInitialLoad, setIsInitialLoad] = useState(false);
  const limit = 100;
  const displayLimit = 100;

  const loadSearchWordsForItem = useCallback(
    async (categoryId: number) => {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("Токен отсутствует");
        return;
      }
      try {
        const response = await fetch("http://127.0.0.1:8000/categories_search_words/search_words_wb_by_category", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ category_ids: [categoryId] }),
        });
        if (response.status === 404) {
          setError("API для ключевых слов по категориям не найден");
          return;
        }
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Не удалось загрузить ключевые слова: ${response.status} ${errorText}`);
        }
        const data: SearchWordsWB[] = await response.json();
        const key = categoryId.toString();
        setSearchWords((prev) => ({
          ...prev,
          [key]: data.sort((a, b) => a.name.localeCompare(b.name)),
        }));
        setError(null);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Неизвестная ошибка");
      }
    },
    []
  );

  const loadGoods = useCallback(async (currentOffset: number) => {
    if (isLoadingGoods || goods.length >= 5735 || isInitialLoad) return;
    setIsLoadingGoods(true);
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Токен отсутствует");
      setIsLoadingGoods(false);
      return;
    }
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/categories_search_words/goods_paginated?offset=${currentOffset}&limit=${limit}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (response.status === 404) {
        setError("API для товаров не найден");
        setIsLoadingGoods(false);
        return;
      }
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Не удалось загрузить товары: ${response.status} ${errorText}`);
      }
      const data: Goods[] = await response.json();
      const newGoods = data.filter((item) => !loadedGoodsIds.has(item.ean13));
      if (newGoods.length > 0) {
        setGoods((prev) => [...prev, ...newGoods]);
        setLoadedGoodsIds((prev) => {
          const newSet = new Set(prev);
          newGoods.forEach((item) => newSet.add(item.ean13));
          return newSet;
        });
        setDisplayedGoods((prev) => [...prev, ...newGoods].slice(0, displayOffset + displayLimit));
      }
      setHasMore(data.length === limit);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка");
    } finally {
      setIsLoadingGoods(false);
      if (!isInitialLoad) setIsInitialLoad(true);
    }
  }, [isLoadingGoods, goods.length, loadedGoodsIds, displayOffset, displayLimit, isInitialLoad]);

  const loadCategories = useCallback(async () => {
    if (isLoadingCategories || categories.length > 0) return;
    setIsLoadingCategories(true);
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Токен отсутствует");
      setIsLoadingCategories(false);
      return;
    }
    try {
      const response = await fetch("http://127.0.0.1:8000/categories_search_words/categories", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.status === 404) {
        setError("API для категорий не найден");
        setIsLoadingCategories(false);
        return;
      }
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Не удалось загрузить категории: ${response.status} ${errorText}`);
      }
      const data: Category[] = await response.json();
      setCategories(data);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка");
    } finally {
      setIsLoadingCategories(false);
    }
  }, [isLoadingCategories, categories.length]);

  const loadCategoryGroups = useCallback(async () => {
    if (isLoadingCategoryGroups || categoryGroups.length > 0) return;
    setIsLoadingCategoryGroups(true);
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Токен отсутствует");
      setIsLoadingCategoryGroups(false);
      return;
    }
    try {
      const response = await fetch("http://127.0.0.1:8000/categories_search_words/categories_with_details", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.status === 404) {
        setError("API для групп категорий не найден");
        setIsLoadingCategoryGroups(false);
        return;
      }
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Не удалось загрузить группы категорий: ${response.status} ${errorText}`);
      }
      const data: CategoryGroup[] = await response.json();
      setCategoryGroups(data.sort((a, b) => a.name.localeCompare(b.name)));
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка");
    } finally {
      setIsLoadingCategoryGroups(false);
    }
  }, [isLoadingCategoryGroups, categoryGroups.length]);

  useEffect(() => {
    loadGoods(0);
    loadCategories();
    loadCategoryGroups();
  }, [loadGoods, loadCategories, loadCategoryGroups]);

  useEffect(() => {
    if (categories.length === 0 || displayedGoods.length === 0) return;
    const allCategoryIds = new Set<number>();
    displayedGoods.forEach((item) => {
      if (!item.categories || item.categories === "-") return;
      const categoryNames = item.categories.split(", ");
      const categoryIds = categoryNames
        .map((name) => categories.find((cat) => cat.name === name)?.id)
        .filter((id): id is number => id !== undefined);
      if (categoryIds.length > 0) allCategoryIds.add(categoryIds[0]);
    });
    const uniqueCategoryIds = Array.from(allCategoryIds);
    uniqueCategoryIds.forEach((id) => loadSearchWordsForItem(id));
  }, [displayedGoods, categories, loadSearchWordsForItem]);

  const handleCategoryChange = async (ean13: string, selectedOption: SingleValue<OptionType> | null) => {
    const categoryId = selectedOption ? selectedOption.value : null;
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Токен отсутствует");
      return;
    }
    try {
      const response = await fetch(`http://127.0.0.1:8000/categories_search_words/goods/${ean13}/category`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ category_ids: categoryId ? [categoryId] : [] }),
      });
      if (response.status === 404) {
        setError("API для обновления категорий не найден");
        return;
      }
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Не удалось обновить категории: ${response.status} ${errorText}`);
      }
      const categoryName = categoryId ? categories.find((c) => c.id === categoryId)?.name : "-";
      setGoods((prev) =>
        prev.map((g) =>
          g.ean13 === ean13 ? { ...g, categories: categoryName } : g
        )
      );
      setDisplayedGoods((prev) =>
        prev.map((g) =>
          g.ean13 === ean13 ? { ...g, categories: categoryName } : g
        )
      );
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка");
    }
  };

  const handleAddSearchWord = useCallback(async (categoryId: number, name: string, source: "table" | "group", key?: string) => {
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Токен отсутствует");
      return;
    }
    if (!name.trim()) {
      setError("Ключевое слово не может быть пустым");
      return;
    }
    try {
      const response = await fetch("http://127.0.0.1:8000/categories_search_words/search_words_wb", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name, category_id: categoryId }),
      });
      if (response.status === 404) {
        setError("API для добавления ключевых слов не найден");
        return;
      }
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Не удалось добавить ключевое слово: ${response.status} ${errorText}`);
      }
      const data: SearchWordsWB = await response.json();
      if (!data.id) throw new Error("Невалидный ответ от сервера");

      const keyForCategory = categoryId.toString();
      setSearchWords((prev) => ({
        ...prev,
        [keyForCategory]: [...(prev[keyForCategory] || []), data].sort((a, b) => a.name.localeCompare(b.name)),
      }));

      if (source === "table" && key) {
        setNewSearchWord((prev) => ({ ...prev, [key]: "" }));
      } else if (source === "group") {
        setNewSearchWord((prev) => ({ ...prev, [categoryId.toString()]: "" }));
      }
      setCategoryGroups((prev) =>
        prev.map((group) =>
          group.id === categoryId
            ? { ...group, search_words: [...group.search_words, data].sort((a, b) => a.name.localeCompare(b.name)) }
            : group
        )
      );
      await loadSearchWordsForItem(categoryId);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка");
    }
  }, [loadSearchWordsForItem]);

  const handleEditSearchWord = useCallback(async (id: number, name: string, categoryId: number) => {
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Токен отсутствует");
      return;
    }
    try {
      const response = await fetch(`http://127.0.0.1:8000/categories_search_words/search_words_wb/${id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name }),
      });
      if (response.status === 404) {
        setError("API для редактирования ключевых слов не найден");
        return;
      }
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Не удалось обновить ключевое слово: ${response.status} ${errorText}`);
      }
      setSearchWords((prev) => {
        const updated = { ...prev };
        const key = categoryId.toString();
        if (updated[key]) {
          updated[key] = updated[key].map((sw) => (sw.id === id ? { ...sw, name } : sw)).sort((a, b) =>
            a.name.localeCompare(b.name)
          );
        }
        return updated;
      });
      setCategoryGroups((prev) =>
        prev.map((group) =>
          group.id === categoryId
            ? {
                ...group,
                search_words: group.search_words.map((sw) => (sw.id === id ? { ...sw, name } : sw)).sort((a, b) => a.name.localeCompare(b.name)),
              }
            : group
        )
      );
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка");
    }
  }, []);

  const handleDeleteSearchWord = useCallback(async (id: number, categoryId: number) => {
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Токен отсутствует");
      return;
    }
    try {
      const response = await fetch(`http://127.0.0.1:8000/categories_search_words/search_words_wb/${id}?category_id=${categoryId}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.status === 404) {
        setError("API для удаления ключевых слов не найден");
        return;
      }
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Не удалось удалить ключевое слово: ${response.status} ${errorText}`);
      }
      setSearchWords((prev) => {
        const updated = { ...prev };
        const key = categoryId.toString();
        if (updated[key]) {
          updated[key] = updated[key].filter((sw) => sw.id !== id);
        }
        return updated;
      });
      setCategoryGroups((prev) =>
        prev.map((group) =>
          group.id === categoryId
            ? { ...group, search_words: group.search_words.filter((sw) => sw.id !== id) }
            : group
        )
      );
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка");
    }
  }, []);

  const handleEditCategoryName = useCallback(async (id: number, name: string) => {
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Токен отсутствует");
      return;
    }
    try {
      const response = await fetch(`http://127.0.0.1:8000/categories_search_words/category/${id}/name`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name }),
      });
      if (response.status === 404) {
        setError("API для редактирования имени категории не найден");
        return;
      }
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Не удалось обновить имя категории: ${response.status} ${errorText}`);
      }
      setCategoryGroups((prev) =>
        prev.map((cg) => (cg.id === id ? { ...cg, name } : cg)).sort((a, b) => a.name.localeCompare(b.name))
      );
      setCategories((prev) =>
        prev.map((c) => (c.id === id ? { ...c, name } : c)).sort((a, b) => a.name.localeCompare(b.name))
      );
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка");
    }
  }, []);

  const handleAddCategory = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (!token || !newCategoryName.trim()) {
      setError("Токен отсутствует или название категории пустое");
      return;
    }
    try {
      const response = await fetch("http://127.0.0.1:8000/categories_search_words/categories", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name: newCategoryName }),
      });
      if (response.status === 404) {
        setError("API для добавления категории не найден");
        return;
      }
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Не удалось добавить категорию: ${response.status} ${errorText}`);
      }
      const data: Category = await response.json();
      setCategories((prev) => [...prev, data].sort((a, b) => a.name.localeCompare(b.name)));
      setCategoryGroups((prev) =>
        [...prev, { id: data.id, name: data.name, search_words: [] }].sort((a, b) =>
          a.name.localeCompare(b.name)
        )
      );
      setNewCategoryName("");
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка");
    }
  }, [newCategoryName]);

  const getSearchWordsByCategories = useCallback(
    (itemCategories: string | undefined): SearchWordsWB[] => {
      if (!itemCategories || itemCategories === "-" || itemCategories.includes(", ")) return [];
      const categoryName = itemCategories;
      const categoryId = categories.find((cat) => cat.name === categoryName)?.id;
      const key = categoryId?.toString() || "";
      return searchWords[key] || [];
    },
    [categories, searchWords]
  );

  const handleLoadMore = () => {
    setOffset((prev) => prev + limit);
    loadGoods(offset + limit);
  };

  const handleLoadMoreDisplay = () => {
    setDisplayOffset((prev) => prev + displayLimit);
    setDisplayedGoods(goods.slice(0, displayOffset + displayLimit));
  };

  const GoodsRow = React.memo(({ item }: { item: Goods }) => {
    const selectedCategory = useMemo(() => {
      return item.categories && item.categories !== "-"
        ? categories
            .filter((cat) => cat.name === item.categories)
            .map((cat) => ({ value: cat.id, label: cat.name }))
        : [];
    }, [item.categories]);

    const searchWordsList = useMemo(() => getSearchWordsByCategories(item.categories), [item.categories]);

    const inputRef = useRef<HTMLInputElement>(null);
    const [localNewWord, setLocalNewWord] = useState("");

    const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
      setLocalNewWord(e.target.value);
    }, []);

    const hasMultipleCategories = !!item.categories && item.categories !== "-" && item.categories.includes(", ");

    return (
      <tr>
        <td>{item.ean13}</td>
        <td>{item.name}</td>
        <td>{item.description || "-"}</td>
        <td>
          <Select
            options={categories.map((cat) => ({ value: cat.id, label: cat.name }))}
            value={selectedCategory.length > 0 ? selectedCategory[0] : null}
            onChange={(selected: SingleValue<OptionType>) => handleCategoryChange(item.ean13, selected)}
            placeholder="Выберите категорию"
            isClearable={true}
            noOptionsMessage={() => "Категории не найдены"}
          />
        </td>
        <td>
          {hasMultipleCategories ? (
            <p style={{ color: "red" }}>Удалите лишнюю категорию</p>
          ) : (
            <>
              <div>
                <input
                  ref={inputRef}
                  type="text"
                  placeholder="Новое ключевое слово"
                  value={localNewWord}
                  onChange={handleInputChange}
                  onFocus={() => inputRef.current?.focus()}
                />
                <button
                  onClick={() => {
                    if (item.categories && !hasMultipleCategories) {
                      const categoryId = categories.find((c) => c.name === item.categories)?.id;
                      if (categoryId) {
                        handleAddSearchWord(categoryId, localNewWord, "table");
                        setLocalNewWord("");
                        inputRef.current?.focus();
                      }
                    }
                  }}
                  disabled={!localNewWord.trim() || hasMultipleCategories}
                >
                  Подтвердить
                </button>
              </div>
              {searchWordsList.map((sw: SearchWordsWB) => (
                <div key={sw.id}>
                  <input
                    type="text"
                    value={sw.name}
                    onChange={(e) => {
                      if (item.categories && !hasMultipleCategories) {
                        const categoryId = categories.find((c) => c.name === item.categories)?.id;
                        if (categoryId) {
                          handleEditSearchWord(sw.id, e.target.value, categoryId);
                        }
                      }
                    }}
                  />
                  <button
                    onClick={() => {
                      if (item.categories && !hasMultipleCategories) {
                        const categoryId = categories.find((c) => c.name === item.categories)?.id;
                        if (categoryId) {
                          handleDeleteSearchWord(sw.id, categoryId);
                        }
                      }
                    }}
                  >
                    Удалить
                  </button>
                </div>
              ))}
            </>
          )}
        </td>
      </tr>
    );
  });

  return (
    <div className="table-container">
      <h1>Категории и ключевые слова</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <h2>Товары</h2>
      <table border={1}>
        <thead>
          <tr>
            <th>EAN13</th>
            <th>Наименование</th>
            <th>Описание</th>
            <th>Категория</th>
            <th>Ключевые слова</th>
          </tr>
        </thead>
        <tbody>
          {displayedGoods.map((item) => (
            <GoodsRow key={item.ean13} item={item} />
          ))}
        </tbody>
      </table>
      {displayedGoods.length < goods.length && (
        <button onClick={handleLoadMoreDisplay}>Показать ещё</button>
      )}
      {hasMore && displayedGoods.length >= goods.length && (
        <button onClick={handleLoadMore}>Загрузить ещё</button>
      )}
      <h2>Добавить новую категорию</h2>
      <div>
        <input
          type="text"
          value={newCategoryName}
          onChange={(e) => setNewCategoryName(e.target.value)}
          placeholder="Название новой категории"
        />
        <button onClick={handleAddCategory} disabled={!newCategoryName.trim()}>
          Добавить
        </button>
      </div>
      <h2>Группы категорий</h2>
      {categoryGroups.map((group) => (
        <div key={group.id}>
          <h3>
            <input
              type="text"
              value={group.name}
              onChange={(e) => handleEditCategoryName(group.id, e.target.value)}
            />
          </h3>
          <h4>Ключевые слова</h4>
          <div>
            <input
              type="text"
              placeholder="Новое ключевое слово"
              value={newSearchWord[group.id.toString()] || ""}
              onChange={(e) => {
                setNewSearchWord((prev) => ({ ...prev, [group.id.toString()]: e.target.value }));
              }}
            />
            <button
              onClick={() => handleAddSearchWord(group.id, newSearchWord[group.id.toString()] || "", "group")}
              disabled={!newSearchWord[group.id.toString()]?.trim()}
            >
              Подтвердить
            </button>
          </div>
          {group.search_words.map((sw: SearchWordsWB) => (
            <div key={sw.id}>
              <input
                type="text"
                value={sw.name}
                onChange={(e) => handleEditSearchWord(sw.id, e.target.value, group.id)}
              />
              <button onClick={() => handleDeleteSearchWord(sw.id, group.id)}>Удалить</button>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

export default CategoriesSearchWords;