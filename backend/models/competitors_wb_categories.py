from sqlalchemy import Column, Integer, ForeignKey
from backend.database import Base

class CompetitorsWBCategory(Base):
    __tablename__ = "competitors_wb_categories"

    id = Column(Integer, primary_key=True, index=True)
    competitors_wb_id = Column(Integer, ForeignKey("competitors_wb.id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)