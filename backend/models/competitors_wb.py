from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.database import Base

class CompetitorsWB(Base):
    __tablename__ = "competitors_wb"

    id = Column(Integer, primary_key=True, index=True)
    hyperlink = Column(String(500), nullable=False)
    name = Column(String(200), nullable=False)
    img_competitors_wb = Column(String(20), nullable=True)

    categories = relationship(
        "Category",
        secondary="competitors_wb_categories"
    )
    search_wb = relationship(
        "SearchWB",
        secondary="search_wb_competitors",
        back_populates="competitors"
    )