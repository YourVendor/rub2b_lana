from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from backend.database import get_db
from backend.models.competitors_wb import CompetitorsWB
from backend.utils import get_current_user
from backend.models.user import User

router = APIRouter(tags=["competitors_wb"])

@router.get("", response_model=list[dict])
async def get_competitors_wb(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    competitors = db.query(CompetitorsWB).options(joinedload(CompetitorsWB.categories)).all()
    return [
        {
            "id": c.id,
            "hyperlink": c.hyperlink,
            "name": c.name,
            "img_competitors_wb": c.img_competitors_wb,
            "categories": [{"id": cat.id, "name": cat.name} for cat in c.categories]
        }
        for c in competitors
    ]