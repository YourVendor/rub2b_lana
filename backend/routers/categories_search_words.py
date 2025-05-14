from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Dict
from backend.database import get_db
from backend.models.goods import Goods
from backend.models.category import Category
from backend.models.search_words_wb import SearchWordsWB
from backend.models.search_wb import SearchWB
from backend.models.goods_categories import GoodsCategory
from backend.models.search_words_wb_categories import SearchWordsWBCategory
from backend.models.search_wb_categories import SearchWBCategory
from backend.utils import get_current_user
from backend.models.user import User

router = APIRouter(tags=["categories_search_words"])

@router.get("/goods_paginated", response_model=List[Dict])
async def get_goods_paginated(
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    goods = (
        db.query(Goods)
        .options(joinedload(Goods.prices))
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        {
            "ean13": g.ean13,
            "name": g.name,
            "description": g.description,
            "categories": ", ".join(
                c.name for c in db.query(Category).join(GoodsCategory).filter(GoodsCategory.goods_ean13 == g.ean13).all()
            ) or "-",
            "stock": g.stock,
            "prices": [
                {
                    "goods_ean13": p.goods_ean13,
                    "company_id": p.company_id,
                    "price_type": p.price_type,
                    "price": p.price,
                }
                for p in g.prices
            ],
        }
        for g in goods
    ]

@router.get("/categories", response_model=List[Dict])
async def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    categories = db.query(Category).all()
    return [{"id": c.id, "name": c.name} for c in categories]

@router.get("/categories_with_details", response_model=List[Dict])
async def get_categories_with_details(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    categories = db.query(Category).all()
    result = []
    for cat in categories:
        search_words = (
            db.query(SearchWordsWB)
            .join(SearchWordsWBCategory)
            .filter(SearchWordsWBCategory.category_id == cat.id)
            .all()
        )
        search_wb = (
            db.query(SearchWB)
            .join(SearchWBCategory)
            .filter(SearchWBCategory.category_id == cat.id)
            .all()
        )
        result.append({
            "id": cat.id,
            "name": cat.name,
            "search_words": [{"id": sw.id, "name": sw.name} for sw in search_words],
            "search_wb": [{"text": sw.text, "frequency_per_month": sw.frequency_per_month} for sw in search_wb],
        })
    return result

@router.patch("/goods/{ean13}/category")
async def update_goods_category(
    ean13: str,
    data: Dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    goods = db.query(Goods).filter(Goods.ean13 == ean13).first()
    if not goods:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    # Удаляем старые категории
    db.query(GoodsCategory).filter(GoodsCategory.goods_ean13 == ean13).delete()
    
    # Добавляем новые
    for cat_id in data.get("category_ids", []):
        if not db.query(Category).filter(Category.id == cat_id).first():
            raise HTTPException(status_code=400, detail=f"Категория {cat_id} не существует")
        db.add(GoodsCategory(goods_ean13=ean13, category_id=cat_id))
    
    db.commit()
    return {"message": "Категории обновлены"}

@router.post("/search_words_wb_by_category", response_model=List[Dict])
async def get_search_words_by_category(
    data: Dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    category_ids = data.get("category_ids", [])
    search_words = (
        db.query(SearchWordsWB)
        .join(SearchWordsWBCategory)
        .filter(SearchWordsWBCategory.category_id.in_(category_ids))
        .all()
    )
    return [{"id": sw.id, "name": sw.name} for sw in search_words]

@router.post("/search_words_wb", response_model=Dict)
async def add_search_word(
    data: Dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    name = data.get("name")
    category_id = data.get("category_id")
    if not name or not category_id:
        raise HTTPException(status_code=400, detail="Название и категория обязательны")
    if not db.query(Category).filter(Category.id == category_id).first():
        raise HTTPException(status_code=400, detail="Категория не существует")

    # Проверяем, существует ли слово
    existing_word = db.query(SearchWordsWB).filter(SearchWordsWB.name == name).first()
    if existing_word:
        search_word = existing_word
    else:
        search_word = SearchWordsWB(name=name)
        db.add(search_word)
        db.flush()

    # Создаём связь
    existing_link = db.query(SearchWordsWBCategory).filter(
        SearchWordsWBCategory.search_words_wb_id == search_word.id,
        SearchWordsWBCategory.category_id == category_id
    ).first()
    if not existing_link:
        new_link = SearchWordsWBCategory(search_words_wb_id=search_word.id, category_id=category_id)
        db.add(new_link)
        db.flush()
        print(f"Created link: search_words_wb_id={search_word.id}, category_id={category_id}, link_id={new_link.id}")
    else:
        print(f"Link already exists: search_words_wb_id={search_word.id}, category_id={category_id}")

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка базы: {str(e)}")
    return {"id": search_word.id, "name": name}

@router.patch("/search_words_wb/{id}")
async def edit_search_word(
    id: int,
    data: Dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    search_word = db.query(SearchWordsWB).filter(SearchWordsWB.id == id).first()
    if not search_word:
        raise HTTPException(status_code=404, detail="Ключевое слово не найдено")
    search_word.name = data.get("name")
    db.commit()
    return {"message": "Ключевое слово обновлено"}

@router.delete("/search_words_wb/{id}")
async def delete_search_word(
    id: int,
    category_id: int,  # Делаем параметр обязательным
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    search_word = db.query(SearchWordsWB).filter(SearchWordsWB.id == id).first()
    if not search_word:
        raise HTTPException(status_code=404, detail="Ключевое слово не найдено")
    
    # Проверяем и удаляем только связь с указанной категорией
    link = db.query(SearchWordsWBCategory).filter(
        SearchWordsWBCategory.search_words_wb_id == id,
        SearchWordsWBCategory.category_id == category_id
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Связь с категорией не найдена")
    
    db.delete(link)
    
    # Проверяем, остались ли другие связи
    other_links = db.query(SearchWordsWBCategory).filter(
        SearchWordsWBCategory.search_words_wb_id == id
    ).count()
    if other_links == 0:
        # Если связей нет, удаляем само слово
        db.delete(search_word)
    
    db.commit()
    return {"message": "Связь удалена"}

@router.patch("/category/{id}/name")
async def update_category_name(
    id: int,
    data: Dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    category.name = data.get("name")
    db.commit()
    return {"message": "Имя категории обновлено"}

@router.post("/categories", response_model=Dict)
async def add_category(
    data: Dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    name = data.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Название категории обязательно")
    category = Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return {"id": category.id, "name": category.name}