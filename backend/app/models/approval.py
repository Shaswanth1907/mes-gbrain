from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.base import Base


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    approval_ref = Column(String, unique=True, nullable=False)
    machine_code = Column(String)
    status = Column(String)
    plan_json = Column(JSONB)
    created_at = Column(DateTime, server_default=func.now())
    approved_at = Column(DateTime, nullable=True)
