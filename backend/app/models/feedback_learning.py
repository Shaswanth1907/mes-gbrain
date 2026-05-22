from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql import func

from app.db.base import Base


class FeedbackLearning(Base):
    __tablename__ = "feedback_learning"

    id = Column(Integer, primary_key=True, index=True)
    machine_code = Column(String)
    action_type = Column(String)

    predicted_downtime = Column(Integer)
    actual_downtime = Column(Integer)

    predicted_technician = Column(String)
    actual_technician = Column(String)

    predicted_part = Column(String)
    actual_part = Column(String)

    success = Column(Boolean)
    notes = Column(Text)

    created_at = Column(DateTime, server_default=func.now())
