from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.routers.utils import get_or_404

router = APIRouter(prefix="/cabinets", tags=["cabinets"])


@router.post("/", response_model=schemas.Cabinet, status_code=status.HTTP_201_CREATED)
def create_cabinet(payload: schemas.CabinetCreate, db: Session = Depends(get_db)):
    get_or_404(db, models.Project, payload.project_id, "Project not found")
    with db.begin():
        cabinet = models.Cabinet(**payload.dict())
        db.add(cabinet)
    db.refresh(cabinet)
    return cabinet


@router.get("/", response_model=list[schemas.Cabinet])
def list_cabinets(db: Session = Depends(get_db), limit: int = 100, offset: int = 0):
    return db.query(models.Cabinet).offset(offset).limit(limit).all()


@router.get("/{cabinet_id}", response_model=schemas.Cabinet)
def get_cabinet(cabinet_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Cabinet, cabinet_id, "Cabinet not found")


@router.put("/{cabinet_id}", response_model=schemas.Cabinet)
def update_cabinet(cabinet_id: int, payload: schemas.CabinetUpdate, db: Session = Depends(get_db)):
    cabinet = get_or_404(db, models.Cabinet, cabinet_id, "Cabinet not found")
    with db.begin():
        for key, value in payload.dict(exclude_unset=True).items():
            setattr(cabinet, key, value)
        db.add(cabinet)
    db.refresh(cabinet)
    return cabinet


@router.delete("/{cabinet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cabinet(cabinet_id: int, db: Session = Depends(get_db)):
    cabinet = get_or_404(db, models.Cabinet, cabinet_id, "Cabinet not found")
    with db.begin():
        db.delete(cabinet)
    return None
