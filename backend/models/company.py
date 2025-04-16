from sqlalchemy import Column, Integer, String
from .user import Base

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    inn = Column(String(12), unique=True, index=True)  # ИНН (12 цифр для РФ)
    name = Column(String(100))
    legal_name = Column(String(200))
    legal_address = Column(String(500))
    actual_address = Column(String(500), nullable=True)