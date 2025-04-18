from sqlalchemy import Column, Integer, DateTime, ForeignKey
from backend.database import Base
from datetime import datetime

class StockHistory(Base):
    __tablename__ = "stock_history"
    id = Column(Integer, primary_key=True, index=True)
    company_item_id = Column(Integer, ForeignKey("company_items.id"), index=True)
    stock = Column(Integer)
    recorded_at = Column(DateTime, default=datetime.utcnow)