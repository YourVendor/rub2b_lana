# backend/models/prices.py
from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class Prices(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    goods_ean13 = Column(String(13), ForeignKey("goods.ean13"), nullable=False)  # Связь с goods по EAN-13
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)  # Связь с companies
    price_type = Column(String(20), nullable=False)  # Тип цены: rrprice, microwholeprice, mediumwholeprice, maxwholeprice
    price = Column(Float, nullable=False)  # Значение цены

    goods = relationship("Goods", back_populates="prices")  # Связь с Goods
    company = relationship("Company", back_populates="prices")  # Связь с Company
    price_history = relationship("PriceHistory", back_populates="price_rel")  # Связь с историей цен