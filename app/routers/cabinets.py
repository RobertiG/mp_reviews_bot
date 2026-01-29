from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db import get_db

router = APIRouter(prefix="/cabinets", tags=["cabinets"])


@router.post("", response_model=schemas.CabinetOut)
def create_cabinet(payload: schemas.CabinetCreate, db: Session = Depends(get_db)):
    return crud.create_cabinet(db, payload.project_id, payload.marketplace, payload.name, payload.api_token)


@router.get("/{project_id}", response_model=list[schemas.CabinetOut])
def list_cabinets(project_id: int, db: Session = Depends(get_db)):
    return crud.list_cabinets(db, project_id)
