from sqlalchemy import Column, ForeignKey, Integer, String

from app.db.base import Base


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)
    work_order_ref = Column(String, unique=True, nullable=False, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    priority = Column(String, nullable=True)
    status = Column(String, nullable=True)
    assigned_to = Column(String, nullable=True)
    escalated_to = Column(String, nullable=True)
