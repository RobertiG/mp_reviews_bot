from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db import get_db

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/{project_id}", response_model=schemas.SettingsOut)
def get_settings(project_id: int, db: Session = Depends(get_db)):
    return crud.get_settings(db, project_id)


@router.put("/{project_id}", response_model=schemas.SettingsOut)
def update_settings(project_id: int, payload: schemas.SettingsUpdate, db: Session = Depends(get_db)):
    return crud.update_settings(db, project_id, payload.model_dump())
