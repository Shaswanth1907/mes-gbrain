from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
import os

from app.db.session import get_db
from app.services.ingestion_service import IngestionService

router = APIRouter()


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    os.makedirs("uploads", exist_ok=True)

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    ingestion = IngestionService(db)

    return ingestion.ingest_uploaded_file(
        file_path=file_path,
        title=file.filename
    )