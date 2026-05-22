import logging

from app.repositories.issue_repository import IssueRepository
from app.repositories.machine_repository import MachineRepository
from app.repositories.maintenance_repository import MaintenanceRepository
from app.repositories.spare_part_repository import SparePartRepository

logger = logging.getLogger("mes_gbrain")


class PredictiveService:
    def __init__(self, db):
        self.machine_repo = MachineRepository(db)
        self.issue_repo = IssueRepository(db)
        self.maintenance_repo = MaintenanceRepository(db)
        self.spare_repo = SparePartRepository(db)

    def predict_failure_risk(self, machine_code):
        try:
            machine = self.machine_repo.get_by_code(machine_code)

            if not machine:
                return {
                    "message": f"Machine {machine_code} not found"
                }

            reasons = []
            score = 0

            open_issues = self.issue_repo.count_open_by_machine(machine.id)

            if open_issues >= 3:
                score += 3
                reasons.append(f"{open_issues} open issues")
            elif open_issues > 0:
                score += 1
                reasons.append(f"{open_issues} open issues")

            maintenance = self.maintenance_repo.recent_by_machine(machine.id)

            overheating_count = sum(
                1 for m in maintenance
                if m.description and "overheat" in m.description.lower()
            )

            if overheating_count >= 2:
                score += 3
                reasons.append(
                    f"{overheating_count} overheating incidents"
                )

            if machine.status == "DOWN":
                score += 2
                reasons.append("machine currently DOWN")

            spare = self.spare_repo.get_by_code("BR-220")

            if spare and spare.quantity <= spare.reorder_level:
                score += 2
                reasons.append("low spare stock for BR-220")

            if score >= 6:
                risk = "HIGH"
            elif score >= 3:
                risk = "MEDIUM"
            else:
                risk = "LOW"

            return {
                "machine_code": machine_code,
                "risk_level": risk,
                "reason": reasons
            }

        except Exception as e:
            logger.error(str(e))
            return {
                "message": "Prediction failed"
            }
