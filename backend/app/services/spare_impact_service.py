from app.services.root_cause_service import RootCauseService
from app.repositories.spare_part_repository import SparePartRepository


class SpareImpactService:
    def __init__(self, db):
        self.root_cause_service = RootCauseService(db)
        self.spare_repo = SparePartRepository(db)

    def assess(self, machine_code):
        root = self.root_cause_service.analyze(machine_code)

        root_cause = (root.get("root_cause") or "").lower()

        part_mapping = {
            "bearing degradation": "BR-220",
            "belt wear": "BLT-101",
            "motor failure": "MTR-500"
        }

        part_code = part_mapping.get(root_cause)

        if not part_code:
            return {
                "machine_code": machine_code,
                "message": "No spare mapping found for predicted root cause"
            }

        part = self.spare_repo.get_by_code(part_code)

        if not part:
            return {
                "machine_code": machine_code,
                "predicted_failure_part": part_code,
                "message": "Required spare part not found in inventory"
            }

        risk = "LOW"
        recommendation = "Spare available. Proceed with maintenance."

        if part.quantity <= part.reorder_level:
            risk = "HIGH"
            recommendation = "Low stock. Immediate procurement recommended."

        elif part.quantity <= (part.reorder_level * 2):
            risk = "MEDIUM"
            recommendation = "Stock is getting low. Plan replenishment."

        return {
            "machine_code": machine_code,
            "predicted_failure_part": part.part_code,
            "part_name": part.part_name,
            "stock_available": part.quantity,
            "reorder_level": part.reorder_level,
            "procurement_risk": risk,
            "recommendation": recommendation
        }
