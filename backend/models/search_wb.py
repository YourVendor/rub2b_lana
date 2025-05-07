from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.database import Base

class SearchWB(Base):
    __tablename__ = "search_wb"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(250), nullable=False)
    frequency_per_month = Column(Integer, nullable=False)

    categories = relationship(
        "Category",
        secondary="search_wb_categories"
    )
    competitors = relationship(
        "CompetitorsWB",
        secondary="search_wb_competitors",
        back_populates="search_wb"
    )