from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware  # Добавь
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import jwt

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://rub2b.ru", "https://www.rub2b.ru"],  # Разреши оба домена
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "твой_секретный_ключ_смени_потом"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

DATABASE_URL = "mysql+mysqlconnector://u3054650_germush:Gremushka27112007@localhost/u3054650_rub2b"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(50), unique=True, index=True)
    password = Column(String(50))

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

@app.get("/")
def root():
    return {"message": "Привет, брат!"}

@app.post("/login")
def login(user: UserIn, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.login == user.login).first()
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    token = jwt.encode({"sub": user.login}, SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}

@app.get("/dashboard", dependencies=[Depends(oauth2_scheme)])
def dashboard():
    return {"message": "Привет, брат! Ты в ЛКVI"}