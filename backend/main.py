from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import jwt
from typing import Optional

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
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(50), unique=True, index=True)
    password = Column(String(50))
    role = Column(String(20), default="retail_client")

class Goods(Base):
    __tablename__ = "goods"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    price = Column(Integer)
    description = Column(String(500), nullable=True)

class Query(Base):
    __tablename__ = "queries"
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(String(1000))
    author = Column(String(50))
    active = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)

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

class QueryIn(BaseModel):
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
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    if payload["role"] != "admin":
        raise HTTPException(status_code=403, detail="Только для админов")
    tables = db.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    return {"tables": [row[0] for row in tables]}

@app.post("/admin/query")
def run_query(query: QueryIn, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    if payload["role"] != "admin":
        raise HTTPException(status_code=403, detail="Только для админов")
    try:
        result = db.execute(query.query_text)
        db.commit()
        return {"result": [dict(row) for row in result]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))