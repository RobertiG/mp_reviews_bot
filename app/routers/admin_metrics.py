from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db import get_db

router = APIRouter(prefix="/admin/metrics", tags=["admin"])


@router.get("", response_model=schemas.AdminMetricsOut)
def admin_metrics(db: Session = Depends(get_db)):
    return crud.metrics(db)
