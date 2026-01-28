from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.routers.utils import get_or_404

router = APIRouter(prefix="/xlsx_upload", tags=["xlsx_upload"])

MAX_FILE_SIZE = 20 * 1024 * 1024


@router.post("/", response_model=schemas.XlsxUpload, status_code=status.HTTP_201_CREATED)
def upload_xlsx(
    project_id: int = Form(..., ge=1),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    get_or_404(db, models.Project, project_id, "Project not found")
    filename = file.filename or ""
    if not filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be .xlsx")
    data = file.file.read()
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")
    with db.begin():
        upload = models.XlsxUpload(
            project_id=project_id,
            filename=filename,
            rows_processed=0,
            rows_failed=0,
        )
        db.add(upload)
    db.refresh(upload)
    return upload


@router.get("/", response_model=list[schemas.XlsxUpload])
def list_uploads(db: Session = Depends(get_db), limit: int = 100, offset: int = 0):
    return db.query(models.XlsxUpload).offset(offset).limit(limit).all()


@router.get("/{upload_id}", response_model=schemas.XlsxUpload)
def get_upload(upload_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.XlsxUpload, upload_id, "Upload not found")


@router.put("/{upload_id}", response_model=schemas.XlsxUpload)
def update_upload(upload_id: int, payload: schemas.XlsxUploadUpdate, db: Session = Depends(get_db)):
    upload = get_or_404(db, models.XlsxUpload, upload_id, "Upload not found")
    with db.begin():
        for key, value in payload.dict(exclude_unset=True).items():
            setattr(upload, key, value)
        db.add(upload)
    db.refresh(upload)
    return upload


@router.delete("/{upload_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_upload(upload_id: int, db: Session = Depends(get_db)):
    upload = get_or_404(db, models.XlsxUpload, upload_id, "Upload not found")
    with db.begin():
        db.delete(upload)
    return None
