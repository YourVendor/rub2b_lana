from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import text
import jwt
from typing import Optional, List
import logging
import pandas as pd
import io
from datetime import datetime, timedelta
from models.user import User
from models.goods import Goods
from models.query import Query
from models.company import Company
from models.warehouse import Warehouse
from models.employee_company import EmployeeCompany
from models.company_item import CompanyItem
from models.price_history import PriceHistory
from models.stock_history import StockHistory
from models.category import Category
from models.goods_categories import GoodsCategory
from models.company_item_categories import CompanyItemCategory
from models.unit import Unit

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
Unit.metadata.create_all(bind=engine)  # Сначала независимые
Category.metadata.create_all(bind=engine)
User.metadata.create_all(bind=engine)
Company.metadata.create_all(bind=engine)
Warehouse.metadata.create_all(bind=engine)
EmployeeCompany.metadata.create_all(bind=engine)
Goods.metadata.create_all(bind=engine)  # Зависит от Unit
CompanyItem.metadata.create_all(bind=engine)  # Зависит от Company, Unit
PriceHistory.metadata.create_all(bind=engine)  # Зависит от CompanyItem
StockHistory.metadata.create_all(bind=engine)  # Зависит от CompanyItem
GoodsCategory.metadata.create_all(bind=engine)  # Зависит от Goods, Category
CompanyItemCategory.metadata.create_all(bind=engine)  # Зависит от CompanyItem, Category
Query.metadata.create_all(bind=engine)  # Независимая

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
    ean13_column: Optional[str] = None
    name_column: str
    unit_column: Optional[str] = None
    price_column: str
    stock_column: str
    skip_first_row: bool = True
    update_missing: str = "zero"  # "zero" or "ignore"
    update_name: bool = False

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
        tables = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        return {"tables": [row[0] for row in tables.fetchall()]}
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
    config: PriceUploadConfig = Depends(),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload["role"] not in ["moderator", "admin"]:
            raise HTTPException(status_code=403, detail="Только для модераторов или админов")
        
        # Читаем Excel
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        if config.skip_first_row:
            df = df.iloc[1:]
        
        # Превью (30 строк)
        preview = df.head(30).to_dict(orient="records")
        
        # Валидация колонок
        required_columns = [config.identifier_column, config.name_column, config.price_column, config.stock_column]
        if config.ean13_column:
            required_columns.append(config.ean13_column)
        if config.unit_column:
            required_columns.append(config.unit_column)
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(status_code=400, detail=f"Отсутствуют колонки: {', '.join(missing_columns)}")
        
        # Обработка прайса
        for _, row in df.iterrows():
            identifier = str(row[config.identifier_column])
            ean13 = str(row[config.ean13_column]) if config.ean13_column and pd.notna(row[config.ean13_column]) else None
            name = str(row[config.name_column])
            unit_id = None
            if config.unit_column and pd.notna(row[config.unit_column]):
                unit = db.query(Unit).filter(Unit.name == str(row[config.unit_column])).first()
                unit_id = unit.id if unit else None
            base_price = float(row[config.price_column])
            stock = int(row[config.stock_column])
            
            # Проверяем существующую позицию
            item = db.query(CompanyItem).filter(
                CompanyItem.company_id == config.company_id,
                CompanyItem.identifier == identifier
            ).first()
            
            if item:
                # Обновляем
                if config.update_name:
                    item.name = name
                item.ean13 = ean13
                item.unit_id = unit_id
                item.base_price = base_price
                item.stock = stock
            else:
                # Создаём новую
                item = CompanyItem(
                    company_id=config.company_id,
                    identifier=identifier,
                    ean13=ean13,
                    name=name,
                    unit_id=unit_id,
                    base_price=base_price,
                    stock=stock
                )
                db.add(item)
                db.flush()  # Получаем item.id
            
            # История цен
            db.add(PriceHistory(company_item_id=item.id, price=base_price))
            # История остатков
            db.add(StockHistory(company_item_id=item.id, stock=stock))
        
        # Обработка отсутствующих позиций
        if config.update_missing == "zero":
            existing_items = db.query(CompanyItem).filter(CompanyItem.company_id == config.company_id).all()
            uploaded_identifiers = set(df[config.identifier_column].astype(str))
            for item in existing_items:
                if item.identifier not in uploaded_identifiers:
                    item.stock = 0
                    db.add(StockHistory(company_item_id=item.id, stock=0))
        
        db.commit()
        return {"preview": preview, "message": "Прайс загружен"}
    except Exception as e:
        logger.error(f"Ошибка в upload_price: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

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
def update_company_item(item_id: int, item_in: CompanyItemIn, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload["role"] not in ["moderator", "admin"]:
            raise HTTPException(status_code=403, detail="Только для модераторов или админов")
        item = db.query(CompanyItem).filter(CompanyItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Позиция не найдена")
        item.ean13 = item_in.ean13
        item.name = item_in.name
        item.unit_id = item_in.unit_id
        item.base_price = item_in.base_price
        item.stock = item_in.stock
        item.price_type = item_in.price_type
        db.add(PriceHistory(company_item_id=item.id, price=item_in.base_price))
        db.add(StockHistory(company_item_id=item.id, stock=item_in.stock))
        db.commit()
        return item
    except Exception as e:
        logger.error(f"Ошибка в update_company_item: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

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