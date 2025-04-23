from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.database import Base
from passlib.context import CryptContext  # Исправлено
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(50), unique=True, index=True)
    password = Column(String(255))
    role = Column(String(20), default="retail_client")  # admin, moderator, employee, retail_client

    employee_companies = relationship("EmployeeCompany", back_populates="user")
    queries = relationship("Query", back_populates="user")
    
    def verify_password(self, plain_password):
        return hashlib.sha256(plain_password.encode()).hexdigest() == self.password