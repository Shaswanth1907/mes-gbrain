from sqlalchemy.orm import Session
from app.models.machine import Machine


class MachineRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(Machine).all()

    def get_running_machines(self):
        return (
            self.db.query(Machine)
            .filter(Machine.status.in_(["RUNNING", "ACTIVE", "active", "running"]))
            .all()
        )

    def get_running(self):
        return (
            self.db.query(Machine)
            .filter(Machine.status.in_(["RUNNING", "ACTIVE", "running", "active"]))
            .all()
        )

    def get_not_running_machines(self):
        return (
            self.db.query(Machine)
            .filter(~Machine.status.in_(["RUNNING", "ACTIVE", "active", "running"]))
            .all()
        )

    def get_by_id(self, machine_id: int):
        return self.db.query(Machine).filter(Machine.id == machine_id).first()

    def get_by_code(self, machine_code: str):
        return self.db.query(Machine).filter(
            Machine.machine_code == machine_code
        ).first()

    def get_by_ref(self, machine_ref: str):
        return self.db.query(Machine).filter(
            Machine.machine_ref == machine_ref
        ).first()

    def create(self, machine_data: dict):
        machine = Machine(**machine_data)
        self.db.add(machine)
        self.db.commit()
        self.db.refresh(machine)
        return machine

    def update_status(self, machine, status):
        machine.status = status
        self.db.commit()
        self.db.refresh(machine)
        return machine
