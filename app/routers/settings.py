from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.routers.utils import get_or_404

router = APIRouter(prefix="/settings", tags=["settings"])


@router.post("/", response_model=schemas.Settings, status_code=status.HTTP_201_CREATED)
def create_settings(payload: schemas.SettingsCreate, db: Session = Depends(get_db)):
    get_or_404(db, models.Project, payload.project_id, "Project not found")
    existing = db.query(models.Settings).filter(models.Settings.project_id == payload.project_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Settings already exist for project")
    with db.begin():
        settings = models.Settings(**payload.dict())
        db.add(settings)
    db.refresh(settings)
    return settings


@router.get("/", response_model=list[schemas.Settings])
def list_settings(db: Session = Depends(get_db), limit: int = 100, offset: int = 0):
    return db.query(models.Settings).offset(offset).limit(limit).all()


@router.get("/{settings_id}", response_model=schemas.Settings)
def get_settings(settings_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Settings, settings_id, "Settings not found")


@router.put("/{settings_id}", response_model=schemas.Settings)
def update_settings(settings_id: int, payload: schemas.SettingsUpdate, db: Session = Depends(get_db)):
    settings = get_or_404(db, models.Settings, settings_id, "Settings not found")
    with db.begin():
        for key, value in payload.dict(exclude_unset=True).items():
            setattr(settings, key, value)
        settings.updated_at = datetime.utcnow()
        db.add(settings)
    db.refresh(settings)
    return settings


@router.delete("/{settings_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_settings(settings_id: int, db: Session = Depends(get_db)):
    settings = get_or_404(db, models.Settings, settings_id, "Settings not found")
    with db.begin():
        db.delete(settings)
    return None
