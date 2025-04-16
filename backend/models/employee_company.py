from sqlalchemy import Column, Integer, ForeignKey
from .user import Base

class EmployeeCompany(Base):
    __tablename__ = "employee_companies"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)