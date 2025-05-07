from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict
import pandas as pd
import aiofiles
import os
import uuid
from datetime import datetime
from backend.database import get_db
from backend.models.search_wb import SearchWB
from backend.models.search_words_wb import SearchWordsWB
from backend.models.category import Category
from backend.models.competitors_wb import CompetitorsWB
from backend.models.search_wb_categories import SearchWBCategories
from backend.models.search_wb_competitors import SearchWBCompetitors
from backend.models.search_words_wb_categories import SearchWordsWBCategories

router = APIRouter()

# Директория для временных файлов
TMP_DIR = "backend/tmp"
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)

# Максимальный размер файла (100 МБ)
MAX_FILE_SIZE = 100 * 1024 * 1024

@router.post("/search_wb/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    category_ids: List[int] = [],
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    if not category_ids:
        raise HTTPException(status_code=400, detail="Выберите хотя бы одну категорию")
    
    # Проверка размера файла
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Файл превышает лимит в 100 МБ")
    
    # Уникальное имя файла
    file_id = str(uuid.uuid4())
    file_path = os.path.join(TMP_DIR, f"upload_{file_id}.csv")
    progress_file = os.path.join(TMP_DIR, f"progress_{file_id}.txt")
    
    # Сохранение файла
    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)
    
    # Кэширование ключевых слов
    query = (
        db.query(SearchWordsWB.name)
        .join(SearchWordsWBCategories)
        .filter(SearchWordsWBCategories.category_id.in_(category_ids))
    )
    keywords = {row.name for row in query.all()}
    if not keywords:
        raise HTTPException(status_code=400, detail="Нет ключевых слов для выбранных категорий")
    
    # Подготовка результата анализа
    analysis = []
    errors = []
    chunk_size = 100000
    total_rows = 0
    processed_rows = 0
    
    # Подсчёт общего количества строк
    with open(file_path, "r", encoding="utf-8") as f:
        total_rows = sum(1 for _ in f) - 1  # Минус заголовок
    
    # Построчная обработка CSV
    for chunk in pd.read_csv(file_path, chunksize=chunk_size, header=None):
        for _, row in chunk.iterrows():
            processed_rows += 1
            try:
                query, freq = row[0].split(",")
                freq = int(freq)
            except (ValueError, IndexError):
                errors.append({"row": row[0], "error": "Невалидный формат строки"})
                continue
            
            if query not in keywords:
                continue
            
            # Проверка существования запроса
            existing = db.query(SearchWB).filter(SearchWB.text == query).first()
            analysis.append({
                "query": query,
                "is_new": existing is None,
                "avg_monthly": existing.frequency_per_month if existing else "новый",
                "new_monthly": freq
            })
        
        # Обновление прогресса
        progress = (processed_rows / total_rows) * 100
        async with aiofiles.open(progress_file, "w") as f:
            await f.write(str(progress))
    
    # Сохранение ошибок
    error_file = None
    if errors:
        error_file_path = os.path.join(TMP_DIR, f"errors_{file_id}.csv")
        pd.DataFrame(errors).to_csv(error_file_path, index=False)
        error_file = f"/tmp/errors_{file_id}.csv"
    
    return {
        "analysis": analysis,
        "file_id": file_id,
        "error_file": error_file
    }

@router.get("/search_wb/upload-status/{file_id}")
async def upload_status(file_id: str):
    progress_file = os.path.join(TMP_DIR, f"progress_{file_id}.txt")
    if not os.path.exists(progress_file):
        return {"progress": 100}
    
    async with aiofiles.open(progress_file, "r") as f:
        progress = await f.read()
    return {"progress": float(progress)}

@router.post("/search_wb/apply-updates")
async def apply_updates(
    file_id: str,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    file_path = os.path.join(TMP_DIR, f"upload_{file_id}.csv")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    updates = []
    inserts = []
    
    # Обработка CSV
    for chunk in pd.read_csv(file_path, chunksize=100000, header=None):
        for _, row in chunk.iterrows():
            try:
                query, freq = row[0].split(",")
                freq = int(freq)
            except (ValueError, IndexError):
                continue
            
            existing = db.query(SearchWB).filter(SearchWB.text == query).first()
            if existing:
                new_freq = round((existing.frequency_per_month + freq) / 2)
                updates.append({"id": existing.id, "frequency_per_month": new_freq})
            else:
                inserts.append({"text": query, "frequency_per_month": freq})
    
    # Пакетное обновление
    if updates:
        for update in updates:
            db.query(SearchWB).filter(SearchWB.id == update["id"]).update(
                {"frequency_per_month": update["frequency_per_month"]}
            )
    
    # Пакетное создание
    if inserts:
        db.bulk_insert_mappings(SearchWB, inserts)
    
    db.commit()
    
    # Удаление временных файлов
    background_tasks.add_task(os.remove, file_path)
    progress_file = os.path.join(TMP_DIR, f"progress_{file_id}.txt")
    if os.path.exists(progress_file):
        background_tasks.add_task(os.remove, progress_file)
    
    return {"message": f"Обновлено: {len(updates)}, Добавлено: {len(inserts)}"}

@router.get("/search_wb")
async def get_search_wb(db: Session = Depends(get_db)):
    results = []
    queries = db.query(SearchWB).all()
    
    for q in queries:
        # Категории
        categories = (
            db.query(Category.name)
            .join(SearchWBCategories)
            .filter(SearchWBCategories.search_wb_id == q.id)
            .all()
        )
        categories = [c.name for c in categories] or ["-"]
        
        # Конкуренты
        competitors = (
            db.query(CompetitorsWB.name, CompetitorsWB.hyperlink)
            .join(SearchWBCompetitors)
            .filter(SearchWBCompetitors.search_wb_id == q.id)
            .all()
        )
        competitors = [{"name": c.name, "hyperlink": c.hyperlink} for c in competitors]
        
        results.append({
            "text": q.text,
            "frequency_per_month": q.frequency_per_month,
            "categories": "/".join(categories),
            "competitors": competitors
        })
    
    return results

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category.id, Category.name).all()
    return [{"id": c.id, "name": c.name} for c in categories]