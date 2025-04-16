from sqlalchemy import Column, Integer, String, Boolean
from .user import Base

class Query(Base):
    __tablename__ = "queries"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))  # Добавляем имя запроса
    query_text = Column(String(1000))
    author = Column(String(50))
    active = Column(Boolean, default=True)