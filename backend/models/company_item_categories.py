from sqlalchemy import Column, Integer, ForeignKey
from backend.database import Base

class CompanyItemCategory(Base):
    __tablename__ = "company_item_categories"
    id = Column(Integer, primary_key=True, index=True)
    company_item_id = Column(Integer, ForeignKey("company_items.id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)