from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.unit import Unit
from backend.utils import get_current_user
from backend.models.user import User

router = APIRouter(tags=["units"])

@router.get("/", response_model=list[dict])
async def get_units(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    units = db.query(Unit).all()
    return [{"id": unit.id, "name": unit.name} for unit in units]