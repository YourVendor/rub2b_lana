from sqlalchemy import Column, Integer, ForeignKey
from backend.database import Base

class SearchWordsWBCategory(Base):
    __tablename__ = "search_words_wb_categories"

    id = Column(Integer, primary_key=True, index=True)
    search_words_wb_id = Column(Integer, ForeignKey("search_words_wb.id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)