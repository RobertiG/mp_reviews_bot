from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.db import get_db

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=schemas.EventOut)
def create_event(payload: schemas.EventCreate, db: Session = Depends(get_db)):
    event, created = crud.create_event(db, payload.model_dump())
    if not created:
        raise HTTPException(status_code=409, detail="Event already exists")
    return event


@router.get("/{project_id}", response_model=list[schemas.EventOut])
def list_events(project_id: int, status: str | None = None, db: Session = Depends(get_db)):
    return crud.list_events(db, project_id, status)


@router.post("/{event_id}/approve")
def approve_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(models.Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Not found")
    event.status = "approved"
    db.commit()
    return {"status": event.status}
