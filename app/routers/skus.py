from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db import get_db

router = APIRouter(prefix="/skus", tags=["skus"])


@router.post("", response_model=schemas.SKUMapOut)
def upsert_sku(payload: schemas.SKUMapCreate, db: Session = Depends(get_db)):
    return crud.upsert_sku_map(
        db,
        payload.project_id,
        payload.marketplace,
        payload.seller_sku,
        payload.marketplace_item_id,
        payload.internal_sku,
        payload.product_name,
    )


@router.get("/{project_id}", response_model=list[schemas.SKUMapOut])
def list_skus(project_id: int, db: Session = Depends(get_db)):
    return crud.list_sku_maps(db, project_id)
