from sqlalchemy import Column, Integer, String, ForeignKey
from backend.database import Base

class GoodsWBGoods(Base):
    __tablename__ = "goods_wb_goods"

    id = Column(Integer, primary_key=True, index=True)
    goods_wb_id = Column(Integer, ForeignKey("goods_wb.id"), primary_key=True)
    goods_ean13 = Column(String(13), ForeignKey("goods.ean13"), primary_key=True)