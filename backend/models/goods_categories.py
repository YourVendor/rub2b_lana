from sqlalchemy import Column, String, Integer, ForeignKey
from backend.database import Base

class GoodsCategory(Base):
    __tablename__ = "goods_categories"
    goods_ean13 = Column(String(13), ForeignKey("goods.ean13"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)