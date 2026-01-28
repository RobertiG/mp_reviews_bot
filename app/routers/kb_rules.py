from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.routers.utils import get_or_404

router = APIRouter(prefix="/kb_rules", tags=["kb_rules"])


@router.post("/", response_model=schemas.KBRule, status_code=status.HTTP_201_CREATED)
def create_kb_rule(payload: schemas.KBRuleCreate, db: Session = Depends(get_db)):
    project = get_or_404(db, models.Project, payload.project_id, "Project not found")
    if payload.sku_id is not None:
        sku = get_or_404(db, models.Sku, payload.sku_id, "Sku not found")
        if sku.project_id != project.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sku does not belong to project")
    with db.begin():
        rule = models.KBRule(**payload.dict())
        db.add(rule)
    db.refresh(rule)
    return rule


@router.get("/", response_model=list[schemas.KBRule])
def list_kb_rules(db: Session = Depends(get_db), limit: int = 100, offset: int = 0):
    return db.query(models.KBRule).offset(offset).limit(limit).all()


@router.get("/{rule_id}", response_model=schemas.KBRule)
def get_kb_rule(rule_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.KBRule, rule_id, "KB rule not found")


@router.put("/{rule_id}", response_model=schemas.KBRule)
def update_kb_rule(rule_id: int, payload: schemas.KBRuleUpdate, db: Session = Depends(get_db)):
    rule = get_or_404(db, models.KBRule, rule_id, "KB rule not found")
    updated = payload.dict(exclude_unset=True)
    if "level" in updated and updated["level"] == schemas.KBLevel.sku and not (
        updated.get("sku_id") or rule.sku_id
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sku_id required for sku-level rules")
    if "sku_id" in updated and updated["sku_id"] is not None:
        sku = get_or_404(db, models.Sku, updated["sku_id"], "Sku not found")
        if sku.project_id != rule.project_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sku does not belong to project")
    with db.begin():
        for key, value in updated.items():
            setattr(rule, key, value)
        db.add(rule)
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kb_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = get_or_404(db, models.KBRule, rule_id, "KB rule not found")
    with db.begin():
        db.delete(rule)
    return None
