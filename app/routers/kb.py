from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db import get_db

router = APIRouter(prefix="/kb", tags=["kb"])


@router.post("", response_model=schemas.KBRuleOut)
def create_rule(payload: schemas.KBRuleCreate, db: Session = Depends(get_db)):
    return crud.create_kb_rule(db, payload.project_id, payload.internal_sku, payload.text)


@router.get("/{project_id}", response_model=list[schemas.KBRuleOut])
def list_rules(project_id: int, db: Session = Depends(get_db)):
    return crud.list_kb_rules(db, project_id)


@router.delete("/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_kb_rule(db, rule_id)
    return {"deleted": bool(deleted)}
