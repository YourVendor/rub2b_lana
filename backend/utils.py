# backend/utils.py
from pydantic import BaseModel, field_validator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
import jwt
from typing import Dict, Any, List, Optional

SECRET_KEY = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # Исправлено

class PriceUploadConfig(BaseModel):
    company_id: int
    identifier_column: str
    ean13_column: str
    name_column: str
    unit_column: str
    rrprice_column: str
    microwholeprice_column: str
    mediumwholeprice_column: str
    maxwholeprice_column: str
    stock_column: str
    skip_first_row: bool
    update_missing: str
    update_name: bool

    @field_validator("update_missing")
    def validate_update_missing(cls, v):
        valid_options = ["zero", "skip", "null", "ignore"]
        if v not in valid_options:
            raise ValueError(f"update_missing must be one of {valid_options}")
        return v

class ConfirmUploadConfig(BaseModel):
    company_id: int
    identifier_column: str
    ean13_column: Optional[str] = None
    name_column: str
    unit_column: str
    rrprice_column: str
    microwholeprice_column: str
    mediumwholeprice_column: str
    maxwholeprice_column: str
    stock_column: str
    skip_first_row: bool
    update_missing: str
    update_name: bool
    confirmed_items: List[Dict[str, Any]]
    ean13_decisions: Dict[str, str]
    unit_mappings: Dict[str, str]
    rows: List[Dict[str, Any]]

    @field_validator("update_missing")
    def validate_update_missing(cls, v):
        valid_options = ["zero", "null", "ignore"]
        if v not in valid_options:
            raise ValueError(f"update_missing must be one of {valid_options}")
        return v

class CompanyItemUpdate(BaseModel):
    identifier: Optional[str] = None
    ean13: Optional[str] = None
    name: Optional[str] = None
    unit_id: Optional[int] = None
    base_price: Optional[float] = None
    stock: Optional[int] = None
    price_type: Optional[str] = None

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалидный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.login == login).first()
    if user is None:
        raise credentials_exception
    return user