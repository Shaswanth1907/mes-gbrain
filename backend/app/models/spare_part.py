from sqlalchemy import Column, Integer, String

from app.db.base import Base


class SparePart(Base):
    __tablename__ = "spare_parts"

    id = Column(Integer, primary_key=True, index=True)
    part_code = Column(String, unique=True, nullable=False)
    part_name = Column(String, nullable=False)
    quantity = Column(Integer, default=0)
    reorder_level = Column(Integer, default=5)
