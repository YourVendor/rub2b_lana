from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class CompanyItem(Base):
    __tablename__ = "company_items"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    identifier = Column(String(50), nullable=True)
    ean13 = Column(String(13), nullable=True)
    name = Column(String(200), nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    brand = Column(String(50), nullable=True)
    rrprice = Column(Float, nullable=False)
    microwholeprice = Column(Float, nullable=True)
    mediumwholeprice = Column(Float, nullable=True)
    maxwholeprice = Column(Float, nullable=True)
    stock = Column(Integer, nullable=True)

    company = relationship("Company", back_populates="items")
    unit = relationship("Unit", back_populates="company_items")