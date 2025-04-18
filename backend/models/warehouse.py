from sqlalchemy import Column, Integer, String, ForeignKey
from backend.database import Base

class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(500))
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)