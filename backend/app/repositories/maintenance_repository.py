from sqlalchemy.orm import Session
from app.models.maintenance import Maintenance


class MaintenanceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_machine_id(self, machine_id: int):
        return (
            self.db.query(Maintenance)
            .filter(Maintenance.machine_id == machine_id)
            .all()
        )

    def get_by_technician(self, technician):
        return (
            self.db.query(Maintenance)
            .filter(Maintenance.technician == technician)
            .all()
        )

    def recent_by_machine(self, machine_id):
        return (
            self.db.query(Maintenance)
            .filter(Maintenance.machine_id == machine_id)
            .all()
        )

    def create(self, maintenance_data: dict):
        maintenance = Maintenance(**maintenance_data)
        self.db.add(maintenance)
        self.db.commit()
        self.db.refresh(maintenance)
        return maintenance
