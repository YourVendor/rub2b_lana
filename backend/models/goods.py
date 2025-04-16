from sqlalchemy import Column, Integer, String
from .user import Base  # Импортируем Base из user.py

class Goods(Base):
    __tablename__ = "goods"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    price = Column(Integer)
    description = Column(String(500), nullable=True)
    category = Column(String(50), nullable=True)
    stock = Column(Integer, default=0)