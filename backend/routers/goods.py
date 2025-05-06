from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from backend.database import get_db
from backend.models.goods import Goods
from backend.utils import get_current_user
from backend.models.user import User

router = APIRouter(tags=["goods"])

@router.get("", response_model=list[dict])
async def get_goods(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    goods = db.query(Goods).options(joinedload(Goods.prices)).all()
    return [
        {
            "ean13": g.ean13,
            "name": g.name,
            "unit_id": g.unit_id,
            "description": g.description,
            "category": g.category,
            "stock": g.stock,
            "prices": [
                {
                    "goods_ean13": p.goods_ean13,
                    "company_id": p.company_id,
                    "price_type": p.price_type,
                    "price": p.price
                }
                for p in g.prices
            ]
        }
        for g in goods
    ]