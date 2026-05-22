from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.db.base import Base


class MonitoringAlert(Base):
    __tablename__ = "monitoring_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_ref = Column(String, unique=True, nullable=False)
    machine_code = Column(String)
    trigger_type = Column(String)
    severity = Column(String)
    message = Column(Text)
    recommendation = Column(Text)
    status = Column(String, default="OPEN")
    created_at = Column(DateTime, server_default=func.now())
