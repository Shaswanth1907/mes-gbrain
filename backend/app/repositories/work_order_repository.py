from sqlalchemy.orm import Session
from app.models.work_order import WorkOrder


class WorkOrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, work_order_data: dict):
        work_order = WorkOrder(**work_order_data)
        self.db.add(work_order)
        self.db.commit()
        self.db.refresh(work_order)
        return work_order

    def get_by_machine_id(self, machine_id: int):
        return (
            self.db.query(WorkOrder)
            .filter(WorkOrder.machine_id == machine_id)
            .all()
        )

    def get_open_by_machine_id(self, machine_id: int):
        return (
            self.db.query(WorkOrder)
            .filter(
                WorkOrder.machine_id == machine_id,
                WorkOrder.status.in_(["OPEN", "IN_PROGRESS"])
            )
            .all()
        )

    def get_open(self):
        return (
            self.db.query(WorkOrder)
            .filter(
                WorkOrder.status.in_([
                    "OPEN",
                    "open",
                    "ACTIVE",
                    "active",
                    "IN_PROGRESS",
                    "in_progress",
                    "PENDING",
                    "pending"
                ])
            )
            .all()
        )

    def get_by_ref(self, work_order_ref: str):
        return (
            self.db.query(WorkOrder)
            .filter(WorkOrder.work_order_ref == work_order_ref)
            .first()
        )

    def get_by_technician(self, technician):
        return (
            self.db.query(WorkOrder)
            .filter(WorkOrder.assigned_to == technician)
            .all()
        )

    def close(self, work_order_ref: str):
        work_order = self.get_by_ref(work_order_ref)

        if not work_order:
            return None

        work_order.status = "CLOSED"
        self.db.commit()
        self.db.refresh(work_order)

        return work_order

    def assign(self, work_order_ref: str, assigned_to: str):
        work_order = self.get_by_ref(work_order_ref)

        if not work_order:
            return None

        work_order.assigned_to = assigned_to
        self.db.commit()
        self.db.refresh(work_order)

        return work_order

    def escalate(self, work_order, escalated_to):
        work_order.status = "ESCALATED"
        work_order.escalated_to = escalated_to
        self.db.commit()
        self.db.refresh(work_order)
        return work_order
