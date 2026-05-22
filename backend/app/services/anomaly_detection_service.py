import logging

from app.services.shift_summary_service import ShiftSummaryService
from app.services.predictive_service import PredictiveService
from app.repositories.machine_repository import MachineRepository

logger = logging.getLogger("mes_gbrain")


class AnomalyDetectionService:
    def __init__(self, db):
        self.shift_service = ShiftSummaryService(db)
        self.predictive_service = PredictiveService(db)
        self.machine_repo = MachineRepository(db)

    def detect(self, machine_code):
        try:
            machine = self.machine_repo.get_by_code(machine_code)

            if not machine:
                return {
                    "message": f"Machine {machine_code} not found"
                }

            summary = self.shift_service.summarize_machine_shift(machine_code)
            risk = self.predictive_service.predict_failure_risk(machine_code)

            shift = summary.get("shift_summary", {})

            anomalies = []
            score = 0

            if machine.status == "DOWN":
                anomalies.append("Machine currently DOWN")
                score += 3

            if (shift.get("downtime_minutes") or 0) > 120:
                anomalies.append("Downtime exceeds threshold")
                score += 2

            if (shift.get("reject_count") or 0) > 50:
                anomalies.append("Reject count unusually high")
                score += 2

            if (shift.get("oee_percent") or 0) < 70:
                anomalies.append("OEE below target")
                score += 2

            if risk.get("risk_level") == "HIGH":
                anomalies.append("Predictive failure risk HIGH")
                score += 3

            severity = "LOW"

            if score >= 6:
                severity = "HIGH"
            elif score >= 3:
                severity = "MEDIUM"

            return {
                "machine_code": machine_code,
                "anomaly_detected": len(anomalies) > 0,
                "anomalies": anomalies,
                "severity": severity,
                "recommendation": (
                    "Immediate investigation required"
                    if severity == "HIGH"
                    else "Monitor machine closely"
                )
            }

        except Exception as e:
            logger.error(f"Anomaly detection failed: {str(e)}")
            return {
                "message": "Anomaly detection failed"
            }
