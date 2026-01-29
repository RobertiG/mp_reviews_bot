from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db import get_db

router = APIRouter(prefix="/balance", tags=["balance"])


@router.get("/{owner_id}", response_model=schemas.BalanceOut)
def get_balance(owner_id: int, db: Session = Depends(get_db)):
    return crud.get_balance(db, owner_id)


@router.post("/{owner_id}", response_model=schemas.BalanceOut)
def update_balance(owner_id: int, payload: schemas.BalanceUpdate, db: Session = Depends(get_db)):
    return crud.update_balance(db, owner_id, payload.delta, payload.reason)
