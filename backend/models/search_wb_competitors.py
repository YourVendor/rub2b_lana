from sqlalchemy import Column, Integer, ForeignKey
from backend.database import Base

class SearchWBCompetitor(Base):
    __tablename__ = "search_wb_competitors"

    id = Column(Integer, primary_key=True, index=True)
    search_wb_id = Column(Integer, ForeignKey("search_wb.id"), primary_key=True)
    competitors_wb_id = Column(Integer, ForeignKey("competitors_wb.id"), primary_key=True)