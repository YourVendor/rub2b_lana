from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from backend.database import Base

class GoodsWB(Base):
    __tablename__ = "goods_wb"

    id = Column(Integer, primary_key=True, index=True)
    article_our = Column(String(60), nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    price = Column(Float, nullable=False)
    name = Column(String(200), nullable=False)

    goods = relationship(
        "Goods",
        secondary="goods_wb_goods",
        back_populates="goods_wb"
    )