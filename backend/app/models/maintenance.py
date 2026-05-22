from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.db.base import Base


class Maintenance(Base):
    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    activity = Column(String, nullable=False)
    description = Column(String, nullable=True)
    technician = Column(String, nullable=True)
    status = Column(String, nullable=True)
    maintenance_date = Column(DateTime(timezone=True), server_default=func.now())
