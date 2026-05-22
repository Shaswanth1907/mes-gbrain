from sqlalchemy.orm import Session

from app.models.production_kpi import ProductionKPI


class ProductionKPIRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_machine_id(self, machine_id: int):
        return (
            self.db.query(ProductionKPI)
            .filter(ProductionKPI.machine_id == machine_id)
            .all()
        )

    def create(self, data: dict):
        kpi = ProductionKPI(**data)
        self.db.add(kpi)
        self.db.commit()
        self.db.refresh(kpi)
        return kpi
