from sqlalchemy import Column, Integer, String
from app.db.base import Base


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    machine_ref = Column(String, unique=True, nullable=False, index=True)
    machine_code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    status = Column(String, nullable=True)