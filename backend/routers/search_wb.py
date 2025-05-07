from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from backend.database import get_db
from backend.models.search_wb import SearchWB
from backend.utils import get_current_user
from backend.models.user import User

router = APIRouter(tags=["search_wb"])

@router.get("", response_model=list[dict])
async def get_search_wb(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    search_wb = db.query(SearchWB).options(
        joinedload(SearchWB.categories),
        joinedload(SearchWB.competitors)
    ).all()
    return [
        {
            "id": sw.id,
            "text": sw.text,
            "frequency_per_month": sw.frequency_per_month,
            "categories": [{"id": c.id, "name": c.name} for c in sw.categories],
            "competitors": [
                {
                    "id": comp.id,
                    "hyperlink": comp.hyperlink,
                    "name": comp.name,
                    "img_competitors_wb": comp.img_competitors_wb
                } for comp in sw.competitors
            ]
        }
        for sw in search_wb
    ]