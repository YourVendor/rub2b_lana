from sqlalchemy import Column, Integer, ForeignKey
from backend.database import Base

class SearchWBCategory(Base):
    __tablename__ = "search_wb_categories"

    id = Column(Integer, primary_key=True, index=True)
    search_wb_id = Column(Integer, ForeignKey("search_wb.id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)