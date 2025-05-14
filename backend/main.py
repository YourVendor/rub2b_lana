# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import get_db
from backend.routers import auth, admin, goods, moderator, units, search_wb, competitors_wb, search_words_wb, goods_wb, categories_search_words
from backend.models.user import Base
from pydantic import BaseModel
from typing import Optional

# Настройка логирования
import logging
logger = logging.getLogger("backend.main")

# Создание движка и сессии
DATABASE_URL = "postgresql+psycopg2://germush:Gremushka27112007@localhost/rub2b"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание таблиц
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(moderator.router, prefix="/moderator", tags=["moderator"])
app.include_router(goods.router, prefix="/goods", tags=["goods"])
app.include_router(units.router, prefix="/units", tags=["units"])
app.include_router(search_wb.router, prefix="/search_wb", tags=["search_wb"])
app.include_router(competitors_wb.router, prefix="/competitors_wb", tags=["competitors_wb"])
app.include_router(search_words_wb.router, prefix="/search_words_wb", tags=["search_words_wb"])
app.include_router(goods_wb.router, prefix="/goods_wb", tags=["goods_wb"])
app.include_router(categories_search_words.router, prefix="/categories_search_words", tags=["categories_search_words"])

# Модели для валидации
class UserIn(BaseModel):
    login: str
    password: str

class GoodsIn(BaseModel):
    ean13: str
    name: str
    unit_id: Optional[int] = None
    description: Optional[str] = None
    category: Optional[str] = None
    stock: int = 0

class QueryIn(BaseModel):
    name: str
    query_text: str
    author: str
    active: bool = True

class CompanyItemIn(BaseModel):
    identifier: str
    ean13: Optional[str] = None
    name: str
    unit_id: Optional[int] = None
    base_price: float
    stock: int
    price_type: Optional[str] = None