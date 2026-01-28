from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.routers.utils import get_or_404

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
def create_project(payload: schemas.ProjectCreate, db: Session = Depends(get_db)):
    with db.begin():
        project = models.Project(**payload.dict())
        db.add(project)
    db.refresh(project)
    return project


@router.get("/", response_model=list[schemas.Project])
def list_projects(db: Session = Depends(get_db), limit: int = 100, offset: int = 0):
    return db.query(models.Project).offset(offset).limit(limit).all()


@router.get("/{project_id}", response_model=schemas.Project)
def get_project(project_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Project, project_id, "Project not found")


@router.put("/{project_id}", response_model=schemas.Project)
def update_project(project_id: int, payload: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    project = get_or_404(db, models.Project, project_id, "Project not found")
    with db.begin():
        for key, value in payload.dict(exclude_unset=True).items():
            setattr(project, key, value)
        db.add(project)
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = get_or_404(db, models.Project, project_id, "Project not found")
    with db.begin():
        db.delete(project)
    return None
