from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.document import Document

router = APIRouter()


@router.get("/documents")
def get_documents(db: Session = Depends(get_db)):
    return db.query(Document).all()


@router.get("/documents/{document_id}")
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document
