from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import text
import jwt
from typing import Optional
import logging
from models.user import User
from models.goods import Goods
from models.query import Query
from models.company import Company
from models.warehouse import Warehouse

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

# Создание таблиц
User.metadata.create_all(bind=engine)
Goods.metadata.create_all(bind=engine)
Query.metadata.create_all(bind=engine)
Company.metadata.create_all(bind=engine)
Warehouse.metadata.create_all(bind=engine)

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
    name: str
    price: int
    description: Optional[str] = None
    category: Optional[str] = None
    stock: int = 0

class QueryIn(BaseModel):
    name: str
    query_text: str
    author: str
    active: bool = True

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
        # Проверяем, есть ли запрос с таким именем и автором
        existing_query = db.query(Query).filter(Query.name == query.name, Query.author == query.author).first()
        if existing_query:
            raise HTTPException(status_code=400, detail=f"Запрос с именем '{query.name}' уже существует")
        # Сохраняем запрос
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
        # Обновляем поля
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