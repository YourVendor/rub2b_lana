from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
import jwt

app = FastAPI()
SECRET_KEY = "твой_секретный_ключ"  # Смени потом!
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class User(BaseModel):
    login: str
    password: str

# Фейковая база (потом MySQL)
fake_users = {"vi": "12345"}

@app.get("/")
def root():
    return {"message": "Привет, брат!"}

@app.post("/login")
def login(user: User):
    if user.login in fake_users and fake_users[user.login] == user.password:
        token = jwt.encode({"sub": user.login}, SECRET_KEY, algorithm="HS256")
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Неверный логин или пароль")