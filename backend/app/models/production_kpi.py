from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer

from app.db.base import Base


class ProductionKPI(Base):
    __tablename__ = "production_kpis"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)

    planned_minutes = Column(Float, default=0)
    runtime_minutes = Column(Float, default=0)
    downtime_minutes = Column(Float, default=0)
    ideal_cycle_time = Column(Float, default=1)

    total_count = Column(Integer, default=0)
    good_count = Column(Integer, default=0)
    reject_count = Column(Integer, default=0)

    kpi_date = Column(DateTime, default=datetime.utcnow)
