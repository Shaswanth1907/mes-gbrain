import logging

from app.repositories.work_order_repository import WorkOrderRepository
from app.repositories.maintenance_repository import MaintenanceRepository

logger = logging.getLogger("mes_gbrain")


class TechnicianService:
    def __init__(self, db):
        self.work_order_repo = WorkOrderRepository(db)
        self.maintenance_repo = MaintenanceRepository(db)

    def get_workload(self, technician):
        try:
            work_orders = self.work_order_repo.get_by_technician(technician)
            maintenance = self.maintenance_repo.get_by_technician(technician)

            return {
                "technician": technician,
                "assigned_work_orders": [
                    {
                        "work_order_ref": w.work_order_ref,
                        "title": w.title,
                        "priority": w.priority,
                        "status": w.status
                    }
                    for w in work_orders
                ],
                "scheduled_maintenance": [
                    {
                        "activity": m.activity,
                        "status": m.status,
                        "maintenance_date": m.maintenance_date
                    }
                    for m in maintenance
                ]
            }

        except Exception as e:
            logger.error(f"Technician workload failed: {str(e)}")
            return {
                "message": "Failed to fetch technician workload"
            }
