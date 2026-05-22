from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    issue_ref = Column(String, unique=True, nullable=False, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    status = Column(String, nullable=True)
    escalated_to = Column(String, nullable=True)
