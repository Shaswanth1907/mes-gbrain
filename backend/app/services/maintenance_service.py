import logging
from datetime import datetime

from app.graph.graph_sync_service import graph_sync
from app.repositories.machine_repository import MachineRepository
from app.repositories.maintenance_repository import MaintenanceRepository

logger = logging.getLogger("mes_gbrain")


class MaintenanceService:
    def __init__(self, db):
        self.db = db
        self.machine_repo = MachineRepository(db)
        self.maintenance_repo = MaintenanceRepository(db)

    def get_history(self, machine_code):
        try:
            machine = self.machine_repo.get_by_code(machine_code)

            if not machine:
                return {
                    "message": f"Machine {machine_code} not found"
                }

            history = self.maintenance_repo.get_by_machine_id(machine.id)

            return {
                "machine_code": machine_code,
                "history": [
                    {
                        "activity": h.activity,
                        "description": h.description,
                        "technician": h.technician,
                        "status": h.status,
                        "maintenance_date": h.maintenance_date
                    }
                    for h in history
                ]
            }

        except Exception as e:
            logger.error(f"History fetch failed: {str(e)}")
            return {"message": "Failed to fetch maintenance history"}

    def create_maintenance(
        self,
        machine_code,
        activity,
        description="",
        technician=""
    ):
        try:
            technician = technician or "Ravi"

            machine = self.machine_repo.get_by_code(machine_code)

            if not machine:
                return {
                    "message": f"Machine {machine_code} not found"
                }

            maintenance = self.maintenance_repo.create({
                "machine_id": machine.id,
                "activity": activity,
                "description": description,
                "technician": technician,
                "status": "SCHEDULED",
                "maintenance_date": datetime.utcnow()
            })

            graph_sync.sync_maintenance(
                maintenance,
                machine.machine_code
            )

            return {
                "message": "Maintenance created successfully",
                "machine_code": machine_code,
                "activity": maintenance.activity,
                "technician": maintenance.technician,
                "status": maintenance.status
            }

        except Exception as e:
            logger.error(f"Maintenance creation failed: {str(e)}")
            return {
                "message": "Failed to create maintenance"
            }
