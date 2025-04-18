from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from backend.database import Base
from datetime import datetime

class PriceHistory(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True, index=True)
    company_item_id = Column(Integer, ForeignKey("company_items.id"), index=True)
    price = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)