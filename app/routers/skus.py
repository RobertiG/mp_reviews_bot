from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.routers.utils import get_or_404

router = APIRouter(prefix="/skus", tags=["skus"])


@router.post("/", response_model=schemas.Sku, status_code=status.HTTP_201_CREATED)
def create_sku(payload: schemas.SkuCreate, db: Session = Depends(get_db)):
    get_or_404(db, models.Project, payload.project_id, "Project not found")
    with db.begin():
        sku = models.Sku(**payload.dict())
        db.add(sku)
    db.refresh(sku)
    return sku


@router.get("/", response_model=list[schemas.Sku])
def list_skus(db: Session = Depends(get_db), limit: int = 100, offset: int = 0):
    return db.query(models.Sku).offset(offset).limit(limit).all()


@router.get("/{sku_id}", response_model=schemas.Sku)
def get_sku(sku_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Sku, sku_id, "Sku not found")


@router.put("/{sku_id}", response_model=schemas.Sku)
def update_sku(sku_id: int, payload: schemas.SkuUpdate, db: Session = Depends(get_db)):
    sku = get_or_404(db, models.Sku, sku_id, "Sku not found")
    with db.begin():
        for key, value in payload.dict(exclude_unset=True).items():
            setattr(sku, key, value)
        db.add(sku)
    db.refresh(sku)
    return sku


@router.delete("/{sku_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sku(sku_id: int, db: Session = Depends(get_db)):
    sku = get_or_404(db, models.Sku, sku_id, "Sku not found")
    with db.begin():
        db.delete(sku)
    return None
