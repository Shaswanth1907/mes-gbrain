import logging

from app.services.predictive_service import PredictiveService
from app.services.root_cause_service import RootCauseService
from app.services.issue_service import IssueService
from app.services.maintenance_service import MaintenanceService
from app.services.spare_part_service import SparePartService

logger = logging.getLogger("mes_gbrain")


class FailureAdvisorService:
    def __init__(self, db):
        self.predictive_service = PredictiveService(db)
        self.root_cause_service = RootCauseService(db)
        self.issue_service = IssueService(db)
        self.maintenance_service = MaintenanceService(db)
        self.spare_service = SparePartService(db)

    def advise(self, machine_code):
        try:
            risk = self.predictive_service.predict_failure_risk(machine_code)
            root = self.root_cause_service.analyze(machine_code)
            issues = self.issue_service.get_open_issues(machine_code)
            maintenance = self.maintenance_service.get_history(machine_code)
            spare = self.spare_service.check_stock("BR-220")

            recommendations = []

            if risk.get("risk_level") == "HIGH":
                recommendations.append(
                    "Immediate maintenance intervention required"
                )

            elif risk.get("risk_level") == "MEDIUM":
                recommendations.append(
                    "Increase monitoring frequency"
                )

            if root.get("root_cause") == "Bearing degradation":
                recommendations.append(
                    "Replace BR-220 bearing immediately"
                )

            if len(issues.get("open_issues", [])) > 0:
                recommendations.append(
                    "Resolve open issues before next shift"
                )

            if len(maintenance.get("history", [])) >= 3:
                recommendations.append(
                    "Review maintenance frequency and preventive schedule"
                )

            if spare.get("quantity", 0) <= spare.get("reorder_level", 0):
                recommendations.append(
                    "Replenish spare inventory for BR-220"
                )

            if not recommendations:
                recommendations.append(
                    "Machine is operating within acceptable reliability limits"
                )

            return {
                "machine_code": machine_code,
                "risk_level": risk.get("risk_level"),
                "root_cause": root.get("root_cause"),
                "recommendations": recommendations
            }

        except Exception as e:
            logger.error(f"Failure advisor failed: {str(e)}")
            return {
                "message": "Failure advisory failed"
            }
