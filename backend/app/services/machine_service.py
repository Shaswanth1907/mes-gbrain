import logging
from app.repositories.machine_repository import MachineRepository
from app.graph.graph_sync_service import graph_sync

logger = logging.getLogger("mes_gbrain")


class MachineService:
    def __init__(self, db):
        self.machine_repo = MachineRepository(db)

    def get_not_running_machines(self):
        try:
            machines = self.machine_repo.get_not_running_machines()

            return {
                "machines": [
                    {
                        "machine_code": machine.machine_code,
                        "machine_ref": machine.machine_ref,
                        "name": machine.name,
                        "location": machine.location,
                        "status": machine.status
                    }
                    for machine in machines
                ]
            }

        except Exception as e:
            logger.error(f"Get not running machines failed: {str(e)}")
            return {
                "message": "Failed to fetch not running machines"
            }

    def get_running_machines(self):
        try:
            machines = self.machine_repo.get_running_machines()

            return {
                "machines": [
                    {
                        "machine_code": machine.machine_code,
                        "machine_ref": machine.machine_ref,
                        "name": machine.name,
                        "location": machine.location,
                        "status": machine.status
                    }
                    for machine in machines
                ]
            }

        except Exception as e:
            logger.error(f"Get running machines failed: {str(e)}")
            return {
                "message": "Failed to fetch running machines"
            }

    def list_machines(self, status=""):
        try:
            machines = self.machine_repo.get_all()

            if status:
                machines = [
                    machine for machine in machines
                    if (machine.status or "").upper() == status.upper()
                ]

            return {
                "machines": [
                    {
                        "machine_code": machine.machine_code,
                        "machine_ref": machine.machine_ref,
                        "name": machine.name,
                        "location": machine.location,
                        "status": machine.status
                    }
                    for machine in machines
                ]
            }

        except Exception as e:
            logger.error(f"List machines failed: {str(e)}")
            return {
                "message": "Failed to fetch machines"
            }

    def get_machine_status(self, machine_code):
        machine = self.machine_repo.get_by_code(machine_code)

        if not machine:
            return {
                "message": f"Machine {machine_code} not found"
            }

        return {
            "machine_code": machine.machine_code,
            "status": machine.status
        }

    def update_machine_status(self, machine_code, status):
        try:
            machine = self.machine_repo.get_by_code(machine_code)

            if not machine:
                return {
                    "message": f"Machine {machine_code} not found"
                }

            updated = self.machine_repo.update_status(
                machine,
                status.upper()
            )

            try:
                graph_sync.sync_machine(updated)
            except Exception as sync_error:
                logger.warning(f"Graph sync failed for machine: {str(sync_error)}")

            return {
                "message": "Machine status updated successfully",
                "machine_code": updated.machine_code,
                "status": updated.status
            }

        except Exception as e:
            logger.error(f"Machine update failed: {str(e)}")
            return {
                "message": "Failed to update machine status"
            }
