import logging

from app.repositories.issue_repository import IssueRepository
from app.repositories.machine_repository import MachineRepository
from app.repositories.maintenance_repository import MaintenanceRepository
from app.repositories.spare_part_repository import SparePartRepository

logger = logging.getLogger("mes_gbrain")


class RootCauseService:
    def __init__(self, db):
        self.machine_repo = MachineRepository(db)
        self.issue_repo = IssueRepository(db)
        self.maintenance_repo = MaintenanceRepository(db)
        self.spare_repo = SparePartRepository(db)

    def analyze(self, machine_code):
        try:
            machine = self.machine_repo.get_by_code(machine_code)

            if not machine:
                return {
                    "message": f"Machine {machine_code} not found"
                }

            issues = self.issue_repo.get_by_machine(machine.id)
            maintenance = self.maintenance_repo.recent_by_machine(machine.id)

            evidence = []
            root_cause = "Unknown"
            recommendation = "Further inspection required"

            overheating_maintenance = [
                m for m in maintenance
                if m.description and "overheat" in m.description.lower()
            ]

            overheating_issues = [
                i for i in issues
                if i.description and "overheat" in i.description.lower()
            ]

            spare = self.spare_repo.get_by_code("BR-220")

            if len(overheating_maintenance) >= 2:
                evidence.append(
                    f"{len(overheating_maintenance)} overheating maintenance incidents"
                )

            if len(overheating_issues) > 0:
                evidence.append(
                    f"{len(overheating_issues)} issue(s) related to overheating"
                )

            if spare and spare.quantity <= spare.reorder_level:
                evidence.append("low spare stock for BR-220")

            if (
                len(overheating_maintenance) >= 2
                and len(overheating_issues) > 0
            ):
                root_cause = "Bearing degradation"
                recommendation = "Immediate bearing inspection/replacement"

            elif machine.status == "DOWN":
                root_cause = "Operational failure"
                recommendation = "Full machine diagnostic required"

            return {
                "machine_code": machine_code,
                "root_cause": root_cause,
                "evidence": evidence,
                "recommendation": recommendation
            }

        except Exception as e:
            logger.error(f"Root cause analysis failed: {str(e)}")
            return {
                "message": "Root cause analysis failed"
            }
