from sqlalchemy import Column, Integer, String, Float, ForeignKey
from backend.database import Base

class CompanyItem(Base):
    __tablename__ = "company_items"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    identifier = Column(String, nullable=False, index=True)
    ean13 = Column(String, nullable=True)
    name = Column(String, nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    base_price = Column(Float, nullable=True)  # Временно возвращаем
    stock = Column(Integer, nullable=True)