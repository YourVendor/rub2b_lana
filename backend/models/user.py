from sqlalchemy import Column, Integer, String
from backend.database import Base  # Исправлено

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(50), unique=True, index=True)
    password = Column(String(50))
    role = Column(String(20), default="retail_client")  # admin, moderator, employee, retail_client