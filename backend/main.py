from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
import logging
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import text
from sqlalchemy import inspect
import jwt
from typing import Optional, List
import logging
import pandas as pd
import json
import io
from datetime import datetime, timedelta
from backend.models.user import User  # Явный импорт
from backend.models.goods import Goods
from backend.models.query import Query
from backend.models.company import Company
from backend.models.warehouse import Warehouse
from backend.models.employee_company import EmployeeCompany
from backend.models.company_item import CompanyItem
from backend.models.price_history import PriceHistory
from backend.models.stock_history import StockHistory
from backend.models.category import Category
from backend.models.goods_categories import GoodsCategory
from backend.models.company_item_categories import CompanyItemCategory
from backend.models.unit import Unit

# Настройка логирования
logger = logging.getLogger("backend.main")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
DATABASE_URL = "postgresql+psycopg2://germush:Gremushka27112007@localhost/rub2b"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание таблиц в правильном порядке
# Unit.metadata.create_all(bind=engine)
# Category.metadata.create_all(bind=engine)
# User.metadata.create_all(bind=engine)
# Company.metadata.create_all(bind=engine)
# Warehouse.metadata.create_all(bind=engine)
# EmployeeCompany.metadata.create_all(bind=engine)
# Goods.metadata.create_all(bind=engine)
# CompanyItem.metadata.create_all(bind=engine)
# PriceHistory.metadata.create_all(bind=engine)
# StockHistory.metadata.create_all(bind=engine)
# GoodsCategory.metadata.create_all(bind=engine)
# CompanyItemCategory.metadata.create_all(bind=engine)
# Query.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

class PriceUploadConfig(BaseModel):
    company_id: int
    identifier_column: str
    ean13_column: str
    name_column: str
    unit_column: str
    rrprice_column: str  # Новое поле
    microwholeprice_column: str  # Новое поле
    mediumwholeprice_column: str  # Новое поле
    maxwholeprice_column: str  # Новое поле
    stock_column: str
    skip_first_row: bool
    update_missing: str
    update_name: bool

    @field_validator("update_missing")
    def validate_update_missing(cls, v):
        valid_options = ["zero", "skip", "null", "ignore"]
        if v not in valid_options:
            raise ValueError(f"update_missing must be one of {valid_options}")
        return v

class CompanyItemUpdate(BaseModel):
    identifier: Optional[str] = None
    ean13: Optional[str] = None
    name: Optional[str] = None
    unit_id: Optional[int] = None
    base_price: Optional[float] = None
    stock: Optional[int] = None
    price_type: Optional[str] = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.get("/")
def root():
    return {"message": "Привет, брат!"}

@app.post("/login")
def login(user: UserIn, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.login == user.login).first()
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    token = jwt.encode({"sub": user.login, "role": db_user.role}, SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}

@app.get("/dashboard")
def dashboard(token: str = Depends(oauth2_scheme)):
    return {"message": "Привет, брат! Ты в дашборде"}

@app.get("/admin/structure")
def get_structure(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload["role"] != "admin":
            raise HTTPException(status_code=403, detail="Только для админов")
        inspector = inspect(db.get_bind())
        tables = inspector.get_table_names()
        return {"tables": tables}
    except Exception as e:
        logger.error(f"Ошибка в get_structure: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/query")
def run_query(query: QueryIn, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload["role"] != "admin":
            raise HTTPException(status_code=403, detail="Только для админов")
        logger.info(f"Выполняется запрос: {query.query_text}")
        result = db.execute(text(query.query_text))
        rows = [dict(row) for row in result.mappings()]
        db.commit()
        existing_query = db.query(Query).filter(Query.name == query.name, Query.author == query.author).first()
        if existing_query:
            raise HTTPException(status_code=400, detail=f"Запрос с именем '{query.name}' уже существует")
        db_query = Query(name=query.name, query_text=query.query_text, author=query.author, active=query.active)
        db.add(db_query)
        db.commit()
        return {"result": rows}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Ошибка в run_query: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/admin/query/{query_id}")
def update_query(query_id: int, query: QueryIn, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload["role"] != "admin":
            raise HTTPException(status_code=403, detail="Только для админов")
        logger.info(f"Обновляется запрос ID {query_id}: {query.query_text}")
        db_query = db.query(Query).filter(Query.id == query_id).first()
        if not db_query:
            raise HTTPException(status_code=404, detail="Запрос не найден")
        result = db.execute(text(query.query_text))
        rows = [dict(row) for row in result.mappings()]
        db.commit()
        db_query.name = query.name
        db_query.query_text = query.query_text
        db_query.author = query.author
        db_query.active = query.active
        db.commit()
        return {"result": rows}
    except Exception as e:
        logger.error(f"Ошибка в update_query: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/admin/queries")
def get_queries(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload["role"] != "admin":
            raise HTTPException(status_code=403, detail="Только для админов")
        queries = db.query(Query).filter(Query.active == True).all()
        return queries
    except Exception as e:
        logger.error(f"Ошибка в get_queries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/admin/query/{query_id}")
def delete_query(query_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload["role"] != "admin":
            raise HTTPException(status_code=403, detail="Только для админов")
        query = db.query(Query).filter(Query.id == query_id).first()
        if not query:
            raise HTTPException(status_code=404, detail="Запрос не найден")
        db.delete(query)
        db.commit()
        return {"message": "Запрос удалён"}
    except Exception as e:
        logger.error(f"Ошибка в delete_query: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/moderator/upload-price")
async def upload_price(
    file: UploadFile = File(...),
    config: str = Form(...),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    logger.info(f"Received file: {file.filename}")
    try:
        config_data = json.loads(config)
        config_obj = PriceUploadConfig(**config_data)
        logger.info(f"Parsed config: {config_obj}")

        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload["role"] != "moderator":
            logger.error(f"User {payload['sub']} is not a moderator")
            raise HTTPException(status_code=403, detail="Только для модераторов")

        user = db.query(User).filter(User.login == payload["sub"]).first()
        if not user:
            logger.error(f"User {payload['sub']} not found")
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        employee = db.query(EmployeeCompany).filter(
            EmployeeCompany.user_id == user.id,
            EmployeeCompany.company_id == config_obj.company_id
        ).first()
        if not employee:
            logger.error(f"Moderator {payload['sub']} not associated with company {config_obj.company_id}")
            raise HTTPException(status_code=403, detail="Вы не связаны с этой компанией")

        company = db.query(Company).filter(Company.id == config_obj.company_id).first()
        if not company:
            logger.error(f"Company with id {config_obj.company_id} not found")
            raise HTTPException(status_code=404, detail=f"Компания с id {config_obj.company_id} не найдена")

        file_content = await file.read()
        excel_buffer = io.BytesIO(file_content)
        df = pd.read_excel(excel_buffer)
        logger.info(f"Excel columns: {list(df.columns)}")

        required_columns = [
            config_obj.identifier_column,
            config_obj.ean13_column,
            config_obj.name_column,
            config_obj.unit_column,
            config_obj.rrprice_column,
            config_obj.microwholeprice_column,
            config_obj.mediumwholeprice_column,
            config_obj.maxwholeprice_column,
            config_obj.stock_column
        ]
        if not all(col in df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            logger.error(f"Missing columns in Excel: {missing}")
            raise HTTPException(status_code=400, detail=f"Отсутствуют колонки: {missing}")

        # Проверка единиц измерения
        units_in_db = {unit.name for unit in db.query(Unit).all()}
        units_in_file = set(df[config_obj.unit_column].dropna().unique())
        unknown_units = list(units_in_file - units_in_db)

        # Обработка ignored_rows
        ignored_rows = []
        if config_obj.update_missing == "skip":
            df = df.dropna(subset=[config_obj.rrprice_column, config_obj.microwholeprice_column,
                                  config_obj.mediumwholeprice_column, config_obj.maxwholeprice_column])
            ignored_rows = df[df[[config_obj.rrprice_column, config_obj.microwholeprice_column,
                                  config_obj.mediumwholeprice_column, config_obj.maxwholeprice_column]].isna().any(axis=1)].to_dict('records')
        elif config_obj.update_missing == "zero":
            df[[config_obj.rrprice_column, config_obj.microwholeprice_column,
                config_obj.mediumwholeprice_column, config_obj.maxwholeprice_column]] = df[[
                config_obj.rrprice_column, config_obj.microwholeprice_column,
                config_obj.mediumwholeprice_column, config_obj.maxwholeprice_column]].fillna(0)
        elif config_obj.update_missing == "null":
            pass  # Оставляем null
        elif config_obj.update_missing == "ignore":
            ignored_rows = df[df[[config_obj.rrprice_column, config_obj.microwholeprice_column,
                                  config_obj.mediumwholeprice_column, config_obj.maxwholeprice_column]].isna().any(axis=1)].to_dict('records')

        preview = df.head(30).to_dict(orient="records")

        return {
            "status": "success",
            "columns": list(df.columns),
            "preview": preview,
            "unknown_units": unknown_units,
            "ignored_rows": ignored_rows
        }
    except HTTPException as e:
        logger.error(f"HTTP error in upload_price: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_price: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/moderator/company-items/{company_id}")
def get_company_items(company_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload["role"] not in ["moderator", "admin"]:
            raise HTTPException(status_code=403, detail="Только для модераторов или админов")
        items = db.query(CompanyItem).filter(CompanyItem.company_id == company_id).all()
        return items
    except Exception as e:
        logger.error(f"Ошибка в get_company_items: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/moderator/company-item/{item_id}")
async def update_company_item(
    item_id: int,
    item_data: CompanyItemUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    logger.info(f"Updating company item {item_id} with data: {item_data}")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload["role"] != "moderator":
            raise HTTPException(status_code=403, detail="Только для модераторов")
        
        item = db.query(CompanyItem).filter(CompanyItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Товар не найден")
        
        for key, value in item_data.model_dump(exclude_unset=True).items():
            if key == "price_type":
                continue
            setattr(item, key, value)
        
        if item_data.price_type == "base":
            item.base_price = item_data.base_price
            db.add(PriceHistory(company_item_id=item.id, price=item_data.base_price))
        
        db.commit()
        db.refresh(item)
        
        return {
            "id": item.id,
            "company_id": item.company_id,
            "identifier": item.identifier,
            "ean13": item.ean13,
            "name": item.name,
            "unit_id": item.unit_id,
            "base_price": item.base_price,
            "stock": item.stock
        }
    except Exception as e:
        logger.error(f"Ошибка в update_company_item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/moderator/average-price/{company_item_id}")
def get_average_price(company_item_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload["role"] not in ["moderator", "admin"]:
            raise HTTPException(status_code=403, detail="Только для модераторов или админов")
        week_ago = datetime.utcnow() - timedelta(days=7)
        prices = db.query(PriceHistory).filter(
            PriceHistory.company_item_id == company_item_id,
            PriceHistory.recorded_at >= week_ago
        ).all()
        if not prices:
            return {"average_price": 0}
        avg_price = sum(p.price for p in prices) / len(prices)
        return {"average_price": avg_price}
    except Exception as e:
        logger.error(f"Ошибка в get_average_price: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))