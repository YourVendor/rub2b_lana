from sqlalchemy import Column, Integer, String, Float, ForeignKey
from .user import Base

class CompanyItem(Base):
    __tablename__ = "company_items"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    identifier = Column(String(100), index=True)  # Временный ID или EAN-13
    ean13 = Column(String(13), nullable=True, index=True)  # Может быть null
    name = Column(String(100))
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    base_price = Column(Float, default=0.0)
    stock = Column(Integer, default=0)
    price_type = Column(String(50), nullable=True)  # Например, "base", "discount_10"