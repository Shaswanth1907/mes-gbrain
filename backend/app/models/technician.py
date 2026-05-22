from sqlalchemy import Column, Integer, String

from app.db.base import Base


class Technician(Base):
    __tablename__ = "technicians"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    skill = Column(String)
    status = Column(String)
