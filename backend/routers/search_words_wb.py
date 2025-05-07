from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from backend.database import get_db
from backend.models.search_words_wb import SearchWordsWB
from backend.utils import get_current_user
from backend.models.user import User

router = APIRouter(tags=["search_words_wb"])

@router.get("", response_model=list[dict])
async def get_search_words_wb(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    search_words = db.query(SearchWordsWB).options(joinedload(SearchWordsWB.categories)).all()
    return [
        {
            "id": sw.id,
            "name": sw.name,
            "categories": [{"id": c.id, "name": c.name} for c in sw.categories]
        }
        for sw in search_words
    ]