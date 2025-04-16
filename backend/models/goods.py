from sqlalchemy import Column, String, Integer, ForeignKey
from .user import Base

class Goods(Base):
    __tablename__ = "goods"
    ean13 = Column(String(13), primary_key=True, index=True)  # EAN-13 вместо id
    name = Column(String(100))
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)  # Связь с единицами измерения
    description = Column(String(500), nullable=True)
    category = Column(String(50), nullable=True)
    stock = Column(Integer, default=0)