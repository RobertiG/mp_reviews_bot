from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.routers.utils import get_or_404

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=schemas.Event, status_code=status.HTTP_201_CREATED)
def create_event(payload: schemas.EventCreate, db: Session = Depends(get_db)):
    project = get_or_404(db, models.Project, payload.project_id, "Project not found")
    cabinet = get_or_404(db, models.Cabinet, payload.cabinet_id, "Cabinet not found")
    if cabinet.project_id != project.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cabinet does not belong to project")
    if payload.sku_id is not None:
        sku = get_or_404(db, models.Sku, payload.sku_id, "Sku not found")
        if sku.project_id != project.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sku does not belong to project")
    with db.begin():
        event = (
            db.query(models.Event)
            .filter(
                models.Event.marketplace_event_id == payload.marketplace_event_id,
                models.Event.marketplace == payload.marketplace.value,
                models.Event.cabinet_id == payload.cabinet_id,
            )
            .first()
        )
        if event:
            return event
        event = models.Event(
            **payload.dict(exclude={"marketplace"}),
            marketplace=payload.marketplace.value,
        )
        db.add(event)
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            existing = (
                db.query(models.Event)
                .filter(
                    models.Event.marketplace_event_id == payload.marketplace_event_id,
                    models.Event.marketplace == payload.marketplace.value,
                    models.Event.cabinet_id == payload.cabinet_id,
                )
                .first()
            )
            if existing:
                return existing
            raise
    db.refresh(event)
    return event


@router.get("/", response_model=list[schemas.Event])
def list_events(db: Session = Depends(get_db), limit: int = 100, offset: int = 0):
    return db.query(models.Event).offset(offset).limit(limit).all()


@router.get("/{event_id}", response_model=schemas.Event)
def get_event(event_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Event, event_id, "Event not found")


@router.put("/{event_id}", response_model=schemas.Event)
def update_event(event_id: int, payload: schemas.EventUpdate, db: Session = Depends(get_db)):
    event = get_or_404(db, models.Event, event_id, "Event not found")
    with db.begin():
        for key, value in payload.dict(exclude_unset=True).items():
            setattr(event, key, value)
        db.add(event)
    db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = get_or_404(db, models.Event, event_id, "Event not found")
    with db.begin():
        db.delete(event)
    return None
