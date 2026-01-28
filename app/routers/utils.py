from fastapi import HTTPException, status
from sqlalchemy.orm import Session


def get_or_404(db: Session, model, obj_id: int, detail: str):
    obj = db.get(model, obj_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return obj
