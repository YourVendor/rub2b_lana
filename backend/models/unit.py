from sqlalchemy import Column, Integer, String
from backend.database import Base  # Исправлено

class Unit(Base):
    __tablename__ = "units"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True)  # шт., м, тыс. шт., уп, кг, г