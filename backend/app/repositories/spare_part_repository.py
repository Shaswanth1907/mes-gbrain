from sqlalchemy.orm import Session

from app.models.spare_part import SparePart


class SparePartRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_code(self, part_code):
        return (
            self.db.query(SparePart)
            .filter(SparePart.part_code == part_code)
            .first()
        )

    def get_low_stock(self):
        return (
            self.db.query(SparePart)
            .filter(SparePart.quantity <= SparePart.reorder_level)
            .all()
        )

    def create(self, data):
        part = SparePart(**data)
        self.db.add(part)
        self.db.commit()
        self.db.refresh(part)
        return part

    def update(self, part):
        self.db.commit()
        self.db.refresh(part)
        return part
