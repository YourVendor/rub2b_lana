from sqlalchemy import Column, Integer, ForeignKey
from .user import Base

class CompanyItemCategory(Base):
    __tablename__ = "company_item_categories"
    company_item_id = Column(Integer, ForeignKey("company_items.id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)