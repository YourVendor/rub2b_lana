from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime

class PriceHistory(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True, index=True)
    price_id = Column(Integer, ForeignKey("prices.id"), nullable=False)
    price_type = Column(String(20), nullable=False)
    price = Column(DOUBLE_PRECISION, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    price_rel = relationship("Prices", back_populates="price_history")