# backend/routers/goods.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.goods import Goods
from backend.utils import get_current_user
from backend.models.user import User

router = APIRouter(tags=["goods"])

@router.get("/", response_model=list[dict])
async def get_goods(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    goods = db.query(Goods).all()
    return [
        {
            "ean13": g.ean13,
            "name": g.name,
            "unit_id": g.unit_id,
            "stock": g.stock,
        }
        for g in goods
    ]