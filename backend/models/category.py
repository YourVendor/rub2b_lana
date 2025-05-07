from sqlalchemy import Column, Integer, String, ForeignKey
from backend.database import Base

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)