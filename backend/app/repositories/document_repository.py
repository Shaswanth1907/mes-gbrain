from sqlalchemy import or_
from app.core.logger import logger
from app.models.document import Document, DocumentChunk


class DocumentRepository:
    def __init__(self, db):
        self.db = db

    def create_document(self, title, content, source_type):
        doc = Document(
            title=title,
            content=content,
            source_type=source_type
        )

        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)

        return doc

    def create_chunk(self, document_id, chunk_text, embedding, metadata=None):
        chunk = DocumentChunk(
            document_id=document_id,
            chunk_text=chunk_text,
            embedding=embedding,
            chunk_metadata=metadata or {}
        )

        self.db.add(chunk)
        self.db.commit()
        self.db.refresh(chunk)

        return chunk

    def search_documents(self, question: str):
        logger.info(f"Searching documents for: {question}")

        return self.db.query(Document).filter(
            or_(
                Document.title.ilike(f"%{question}%"),
                Document.content.ilike(f"%{question}%")
            )
        ).limit(5).all()