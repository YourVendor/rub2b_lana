from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    goods = relationship(
        "Goods",
        secondary="goods_categories",
        back_populates="categories"
    )
    search_words_wb = relationship(
        "SearchWordsWB",
        secondary="search_words_wb_categories",
        back_populates="categories"
    )