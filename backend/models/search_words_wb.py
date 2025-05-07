from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.database import Base

class SearchWordsWB(Base):
    __tablename__ = "search_words_wb"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    categories = relationship(
        "Category",
        secondary="search_words_wb_categories"
    )