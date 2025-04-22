import os
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form, Response, status
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
import logging
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, func, and_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import text
from sqlalchemy import inspect
import jwt
from typing import Optional, Dict, Any, List
import logging
from fastapi.responses import FileResponse
import pandas as pd
import tempfile
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
from backend.database import get_db

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
ALGORITHM = "HS256"
DATABASE_URL = "postgresql+psycopg2://germush:Gremushka27112007@localhost/rub2b"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалидный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.login == login).first()
    if user is None:
        raise credentials_exception
    return user

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

class ConfirmUploadConfig(BaseModel):
    company_id: int
    identifier_column: str
    ean13_column: Optional[str] = None
    name_column: str
    unit_column: str
    rrprice_column: str
    microwholeprice_column: str
    mediumwholeprice_column: str
    maxwholeprice_column: str
    stock_column: str
    skip_first_row: bool
    update_missing: str
    update_name: bool
    confirmed_items: List[Dict[str, Any]]
    ean13_decisions: Dict[str, str]
    unit_mappings: Dict[str, str]
    rows: List[Dict[str, Any]]

    @field_validator("update_missing")
    def validate_update_missing(cls, v):
        valid_options = ["zero", "null", "ignore"]
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
async def execute_query(query_text: str, name: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_current_user(token, db)  # Исправляем, добавляем db
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    
    # Проверяем, существует ли запрос с таким именем и автором
    existing_query = db.query(Query).filter(Query.name == name, Query.author == user.login).first()
    if existing_query:
        raise HTTPException(status_code=400, detail="Запрос с таким именем уже существует")
    
    try:
        result = db.execute(text(query_text)).fetchall()
        query = Query(name=name, query_text=query_text, author=user.login, active=True)
        db.add(query)
        db.commit()
        return {"results": [dict(row) for row in result], "message": "Запрос выполнен и сохранён"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Ошибка выполнения запроса: {str(e)}")

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
        units_in_file = set(df[config_obj.unit_column].dropna().astype(str))
        unknown_units = list(units_in_file - units_in_db)

        # Обработка ignored_rows
        ignored_rows = []
        if config_obj.update_missing == "skip":
            df = df.dropna(subset=[config_obj.rrprice_column, config_obj.microwholeprice_column,
                                  config_obj.mediumwholeprice_column, config_obj.maxwholeprice_column])
            ignored_rows = df[df[[config_obj.rrprice_column, config_obj.microwholeprice_column,
                                  config_obj.mediumwholeprice_column, config_obj.maxwholeprice_column]].isna().any(axis=1)].to_dict(orient='records')
        elif config_obj.update_missing == "zero":
            df[[config_obj.rrprice_column, config_obj.microwholeprice_column,
                config_obj.mediumwholeprice_column, config_obj.maxwholeprice_column]] = df[[
                config_obj.rrprice_column, config_obj.microwholeprice_column,
                config_obj.mediumwholeprice_column, config_obj.maxwholeprice_column]].fillna(0)
        elif config_obj.update_missing == "null":
            pass  # Оставляем null
        elif config_obj.update_missing == "ignore":
            ignored_rows = df[df[[config_obj.rrprice_column, config_obj.microwholeprice_column,
                                  config_obj.mediumwholeprice_column, config_obj.maxwholeprice_column]].isna().any(axis=1)].to_dict(orient='records')

        preview = df.to_dict(orient="records")
        logger.info(f"Preview rows: {len(preview)}")

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
        return [
            {
                "id": item.id,
                "company_id": item.company_id,
                "identifier": item.identifier,
                "ean13": item.ean13,
                "name": item.name,
                "unit_id": item.unit_id,
                "rrprice": item.rrprice,
                "microwholeprice": item.microwholeprice,
                "mediumwholeprice": item.mediumwholeprice,
                "maxwholeprice": item.maxwholeprice,
                "stock": item.stock
            }
            for item in items
        ]
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

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(tempfile.gettempdir(), filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(file_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=filename)

@app.post("/moderator/confirm-upload")
async def confirm_upload(
    file: UploadFile = File(...),
    config: str = Form(...),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    logger.info(f"Received confirm-upload for file: {file.filename}")
    try:
        config_data = json.loads(config)
        config_obj = ConfirmUploadConfig(**config_data)
        logger.info(f"Parsed config: {config_obj}")
        logger.info(f"Confirmed items: {config_obj.confirmed_items}")

        # Проверка авторизации
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload["role"] != "moderator":
            raise HTTPException(status_code=403, detail="Только для модераторов")
        user = db.query(User).filter(User.login == payload["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        employee = db.query(EmployeeCompany).filter(
            EmployeeCompany.user_id == user.id,
            EmployeeCompany.company_id == config_obj.company_id
        ).first()
        if not employee:
            raise HTTPException(status_code=403, detail="Вы не связаны с этой компанией")
        company = db.query(Company).filter(Company.id == config_obj.company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail=f"Компания с id {config_obj.company_id} не найдена")

        # Чтение файла
        file_content = await file.read()
        excel_buffer = io.BytesIO(file_content)
        df = pd.read_excel(excel_buffer)
        if config_obj.skip_first_row:
            df = df.iloc[1:]
        df[config_obj.identifier_column] = df[config_obj.identifier_column].astype(str)
        logger.info(f"Excel rows: {len(df)}, columns: {list(df.columns)}")

        # Проверка размера
        if len(df) > 10000:
            raise HTTPException(status_code=400, detail="Слишком много позиций, максимум 10,000")

        # Маппинг единиц измерения
        units_in_db = {unit.name: unit.id for unit in db.query(Unit).all()}
        logger.info(f"Units in DB: {units_in_db}")
        non_uploaded_items = []
        processed_rows = []

        # Обработка дублей identifier
        identifier_counts = df[config_obj.identifier_column].value_counts()
        duplicates = identifier_counts[identifier_counts > 1].index.tolist()
        selected_duplicates = {}
        for dup in duplicates:
            dup_rows = df[df[config_obj.identifier_column] == dup].to_dict("records")
            selected_row = next(
                (row for row in dup_rows if row.get("selected")),  # Предполагается выбор фронтом
                dup_rows[-1]  # По умолчанию последняя
            )
            selected_duplicates[dup] = selected_row
            non_uploaded_items.extend(
                [{"identifier": dup, "reason": "Дубликат identifier, выбрана другая строка", **row}
                 for row in dup_rows if row != selected_row]
            )
        logger.info(f"Duplicates found: {duplicates}")

        # Обработка всех строк из файла
        logger.info(f"Processing {len(df)} rows")
        for _, row in df.iterrows():
            identifier = str(row[config_obj.identifier_column])
            unit = str(row[config_obj.unit_column]) if row[config_obj.unit_column] else None
            prices = {
                "rrprice": row[config_obj.rrprice_column],
                "microwholeprice": row[config_obj.microwholeprice_column],
                "mediumwholeprice": row[config_obj.mediumwholeprice_column],
                "maxwholeprice": row[config_obj.maxwholeprice_column]
            }
            stock = row[config_obj.stock_column]
            name = str(row[config_obj.name_column]) if row[config_obj.name_column] else None
            ean13 = row.get(config_obj.ean13_column, None)
            logger.info(f"Processing row: identifier={identifier}, unit={unit}, ean13={ean13}")

            # Проверка цен
            if any(price is not None and price < 0 for price in prices.values()):
                non_uploaded_items.append({
                    "identifier": identifier, "reason": "Отрицательная цена", **row.to_dict()
                })
                logger.info(f"Rejected: {identifier} - Отрицательная цена")
                continue
            if any(price == 0 or pd.isna(price) for price in prices.values()):
                if config_data.get("zero_price_action", "ignore") == "error":
                    non_uploaded_items.append({
                        "identifier": identifier, "reason": "Пустая/нулевая цена", **row.to_dict()
                    })
                    logger.info(f"Rejected: {identifier} - Пустая/нулевая цена")
                continue

            # Проверка unit
            mapped_unit = config_obj.unit_mappings.get(unit, unit)
            if mapped_unit == "ignore" or mapped_unit not in units_in_db:
                non_uploaded_items.append({
                    "identifier": identifier, "reason": f"Неизвестная единица измерения: {unit}", **row.to_dict()
                })
                logger.info(f"Rejected: {identifier} - Неизвестная единица измерения: {unit}")
                continue
            unit_id = units_in_db[mapped_unit]

            # Проверка EAN-13
            if ean13 is not None:
                ean13_str = str(ean13).strip()
                if not (len(ean13_str) == 13 and ean13_str.isdigit()):
                    non_uploaded_items.append({
                        "identifier": identifier, "reason": f"Невалидный EAN-13: {ean13}", **row.to_dict()
                    })
                    logger.info(f"Rejected: {identifier} - Невалидный EAN-13: {ean13}")
                    continue
                ean13 = ean13_str

            # Проверка существования
            existing_item = db.query(CompanyItem).filter(
                and_(CompanyItem.company_id == config_obj.company_id, CompanyItem.identifier == identifier)
            ).first()

            if existing_item:
                # Обновление
                ean13_decision = config_obj.ean13_decisions.get(identifier, "keep")
                if ean13_decision == "update" and ean13:
                    existing_item.ean13 = ean13
                if config_obj.update_name:
                    existing_item.name = name
                existing_item.rrprice = prices["rrprice"]
                existing_item.microwholeprice = prices["microwholeprice"]
                existing_item.mediumwholeprice = prices["mediumwholeprice"]
                existing_item.maxwholeprice = prices["maxwholeprice"]
                existing_item.stock = stock
                processed_rows.append({"identifier": identifier, "action": "updated"})
                logger.info(f"Updated: {identifier}")
            else:
                # Добавление (убрали проверку confirmed_items)
                new_item = CompanyItem(
                    company_id=config_obj.company_id,
                    identifier=identifier,
                    name=name,
                    ean13=ean13,
                    unit_id=unit_id,
                    rrprice=prices["rrprice"],
                    microwholeprice=prices["microwholeprice"],
                    mediumwholeprice=prices["mediumwholeprice"],
                    maxwholeprice=prices["maxwholeprice"],
                    stock=stock
                )
                db.add(new_item)
                processed_rows.append({"identifier": identifier, "action": "added"})
                logger.info(f"Added: {identifier}")

        # Обработка отсутствующих позиций
        existing_identifiers = db.query(CompanyItem.identifier).filter(
            CompanyItem.company_id == config_obj.company_id
        ).all()
        existing_identifiers = {x[0] for x in existing_identifiers}
        file_identifiers = set(df[config_obj.identifier_column])
        missing_identifiers = existing_identifiers - file_identifiers
        missing_processed = []
        for identifier in missing_identifiers:
            item = db.query(CompanyItem).filter(
                and_(CompanyItem.company_id == config_obj.company_id, CompanyItem.identifier == identifier)
            ).first()
            if config_obj.update_missing == "zero":
                item.stock = 0
                missing_processed.append({"identifier": identifier, "action": "zeroed"})
            elif config_obj.update_missing == "null":
                item.stock = None
                item.rrprice = None
                item.microwholeprice = None
                item.mediumwholeprice = None
                item.maxwholeprice = None
                missing_processed.append({"identifier": identifier, "action": "nulled"})
            else:  # ignore
                missing_processed.append({"identifier": identifier, "action": "ignored"})
        logger.info(f"Missing identifiers processed: {len(missing_processed)}")

        # Сохранение изменений
        db.commit()

        # Формирование Excel с ошибками
        error_file = None
        message = "Обработка завершена успешно, ошибок нет"
        if non_uploaded_items:
            error_df = pd.DataFrame(non_uploaded_items)
            logger.info(f"Non-uploaded items: {len(non_uploaded_items)}")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                error_df.to_excel(tmp.name, index=False)
                error_file = os.path.basename(tmp.name)
            message = f"Обработка завершена, найдено ошибок: {len(non_uploaded_items)}"
        else:
            logger.info("No non-uploaded items to save")

        return {
            "status": "success",
            "message": message,
            "updated": len([r for r in processed_rows if r["action"] == "updated"]),
            "added": len([r for r in processed_rows if r["action"] == "added"]),
            "ignored": len([r for r in processed_rows if r["action"] == "ignored"]),
            "missing_processed": missing_processed,
            "error_file": f"/download/{error_file}" if error_file else None
        }
    except HTTPException as e:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error in confirm_upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/moderator/companies")
async def get_companies(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_current_user(token, db)
    companies = db.query(Company).join(EmployeeCompany).filter(EmployeeCompany.user_id == user.id).all()
    return Response(
        content=json.dumps([{"id": c.id, "name": c.name, "inn": c.inn} for c in companies], ensure_ascii=False),
        media_type="application/json; charset=utf-8"
    )
    
@app.get("/units")
async def get_units(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_current_user(token, db)
    units = db.query(Unit).all()
    return Response(
        content=json.dumps([{"id": u.id, "name": u.name} for u in units], ensure_ascii=False),
        media_type="application/json; charset=utf-8"
    )