from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.routers.utils import get_or_404

router = APIRouter(prefix="/balance", tags=["balance"])


@router.post("/", response_model=schemas.Balance, status_code=status.HTTP_201_CREATED)
def create_balance(payload: schemas.BalanceCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Balance).filter(models.Balance.owner_id == payload.owner_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Balance already exists for owner")
    with db.begin():
        balance = models.Balance(**payload.dict())
        db.add(balance)
    db.refresh(balance)
    return balance


@router.get("/", response_model=list[schemas.Balance])
def list_balances(db: Session = Depends(get_db), limit: int = 100, offset: int = 0):
    return db.query(models.Balance).offset(offset).limit(limit).all()


@router.get("/{balance_id}", response_model=schemas.Balance)
def get_balance(balance_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Balance, balance_id, "Balance not found")


@router.put("/{balance_id}", response_model=schemas.Balance)
def update_balance(balance_id: int, payload: schemas.BalanceUpdate, db: Session = Depends(get_db)):
    balance = get_or_404(db, models.Balance, balance_id, "Balance not found")
    with db.begin():
        balance.tokens = payload.tokens
        balance.updated_at = datetime.utcnow()
        db.add(balance)
    db.refresh(balance)
    return balance


@router.delete("/{balance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_balance(balance_id: int, db: Session = Depends(get_db)):
    balance = get_or_404(db, models.Balance, balance_id, "Balance not found")
    with db.begin():
        db.delete(balance)
    return None
