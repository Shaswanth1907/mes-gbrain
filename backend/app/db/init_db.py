from app.db.base import Base
from app.db.session import engine

from app.models.machine import Machine
from app.models.issue import Issue
from app.models.document import Document, DocumentChunk


def create_tables():
    Base.metadata.create_all(bind=engine)