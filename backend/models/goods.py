from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class Goods(Base):
    __tablename__ = "goods"
    ean13 = Column(String(13), primary_key=True, unique=True, index=True)
    name = Column(String(100))
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    description = Column(String(500), nullable=True)
    category = Column(String(50), nullable=True)
    brand = Column(String(50), nullable=True)
    stock = Column(Integer, default=0)

    prices = relationship("Prices", back_populates="goods")
    unit = relationship("Unit", back_populates="goods")
    # Добавлена связь с GoodsWB
    goods_wb = relationship(
        "GoodsWB",
        secondary="goods_wb_goods",
        back_populates="goods"
    )