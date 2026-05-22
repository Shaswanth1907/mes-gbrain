from app.services.autonomous_maintenance_planner import AutonomousMaintenancePlanner
from app.services.work_order_service import WorkOrderService
from app.services.maintenance_service import MaintenanceService
from app.repositories.spare_part_repository import SparePartRepository


class ExecuteCorrectivePlanService:
    def __init__(self, db):
        self.db = db
        self.planner = AutonomousMaintenancePlanner(db)
        self.work_order_service = WorkOrderService(db)
        self.maintenance_service = MaintenanceService(db)
        self.spare_repo = SparePartRepository(db)

    def execute(self, machine_code):
        plan = self.planner.plan(machine_code)

        executed = []

        wo = self.work_order_service.create_work_order(
            machine_code=machine_code,
            description=plan["recommended_action"],
            priority=plan["priority"]
        )

        if wo.get("work_order_ref"):
            executed.append({
                "action": "Work order created",
                "work_order_ref": wo["work_order_ref"]
            })

        root = plan["root_cause"]

        part_map = {
            "Bearing degradation": "BR-220",
            "Belt wear": "BLT-101",
            "Motor failure": "MTR-500"
        }

        part_code = part_map.get(root)

        if part_code:
            part = self.spare_repo.get_by_code(part_code)

            if part:
                part.quantity -= 1
                self.db.commit()
                self.db.refresh(part)

                executed.append({
                    "action": "Spare reserved",
                    "part_code": part.part_code,
                    "remaining_stock": part.quantity
                })

        self.maintenance_service.create_maintenance(
            machine_code=machine_code,
            activity="Corrective Maintenance",
            description=plan["recommended_action"],
            technician=plan["assigned_technician"]
        )

        executed.append({
            "action": "Maintenance scheduled",
            "technician": plan["assigned_technician"]
        })

        return {
            "machine_code": machine_code,
            "execution_status": "SUCCESS",
            "actions_executed": executed
        }
