from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.routers.utils import get_or_404

router = APIRouter(prefix="/admin_metrics", tags=["admin_metrics"])


@router.post("/", response_model=schemas.AdminMetric, status_code=status.HTTP_201_CREATED)
def create_admin_metric(payload: schemas.AdminMetricCreate, db: Session = Depends(get_db)):
    get_or_404(db, models.Project, payload.project_id, "Project not found")
    with db.begin():
        metric = models.AdminMetric(**payload.dict())
        db.add(metric)
    db.refresh(metric)
    return metric


@router.get("/", response_model=list[schemas.AdminMetric])
def list_admin_metrics(db: Session = Depends(get_db), limit: int = 100, offset: int = 0):
    return db.query(models.AdminMetric).offset(offset).limit(limit).all()


@router.get("/{metric_id}", response_model=schemas.AdminMetric)
def get_admin_metric(metric_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.AdminMetric, metric_id, "Admin metric not found")


@router.put("/{metric_id}", response_model=schemas.AdminMetric)
def update_admin_metric(metric_id: int, payload: schemas.AdminMetricUpdate, db: Session = Depends(get_db)):
    metric = get_or_404(db, models.AdminMetric, metric_id, "Admin metric not found")
    with db.begin():
        for key, value in payload.dict(exclude_unset=True).items():
            setattr(metric, key, value)
        db.add(metric)
    db.refresh(metric)
    return metric


@router.delete("/{metric_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_metric(metric_id: int, db: Session = Depends(get_db)):
    metric = get_or_404(db, models.AdminMetric, metric_id, "Admin metric not found")
    with db.begin():
        db.delete(metric)
    return None
