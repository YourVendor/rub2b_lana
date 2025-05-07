from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from backend.database import get_db
from backend.models.goods_wb import GoodsWB
from backend.utils import get_current_user
from backend.models.user import User

router = APIRouter(tags=["goods_wb"])

@router.get("", response_model=list[dict])
async def get_goods_wb(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    goods_wb = db.query(GoodsWB).options(joinedload(GoodsWB.goods)).all()
    return [
        {
            "id": g.id,
            "article_our": g.article_our,
            "stock": g.stock,
            "price": g.price,
            "name": g.name,
            "goods": [
                {
                    "ean13": good.ean13,
                    "name": good.name,
                    "stock": good.stock
                } for good in g.goods
            ]
        }
        for g in goods_wb
    ]