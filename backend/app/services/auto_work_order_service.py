import logging

from app.services.predictive_service import PredictiveService
from app.services.root_cause_service import RootCauseService
from app.services.shift_summary_service import ShiftSummaryService
from app.services.issue_service import IssueService
from app.services.work_order_service import WorkOrderService

logger = logging.getLogger("mes_gbrain")


class AutoWorkOrderService:
    def __init__(self, db):
        self.predictive_service = PredictiveService(db)
        self.root_cause_service = RootCauseService(db)
        self.shift_service = ShiftSummaryService(db)
        self.issue_service = IssueService(db)
        self.work_order_service = WorkOrderService(db)

    def recommend(self, machine_code):
        try:
            risk = self.predictive_service.predict_failure_risk(machine_code)
            root = self.root_cause_service.analyze(machine_code)
            shift = self.shift_service.summarize_machine_shift(machine_code)
            issues = self.issue_service.get_open_issues(machine_code)

            reasons = []
            priority = "MEDIUM"
            should_create = False

            if risk.get("risk_level") in ["HIGH", "MEDIUM"]:
                reasons.append(
                    f"Predictive risk is {risk.get('risk_level')}"
                )
                should_create = True

            if root.get("root_cause") != "Unknown":
                reasons.append(
                    f"Root cause indicates {root.get('root_cause')}"
                )
                should_create = True

            if len(issues.get("open_issues", [])) > 0:
                reasons.append("Open issue exists")
                should_create = True

            oee = shift.get("shift_summary", {}).get("oee_percent", 100)

            if oee < 70:
                reasons.append("OEE below target")
                priority = "URGENT"

            return {
                "machine_code": machine_code,
                "should_create_work_order": should_create,
                "reason": reasons,
                "recommended_priority": priority
            }

        except Exception as e:
            logger.error(f"Recommendation failed: {str(e)}")
            return {
                "message": "Recommendation failed"
            }

    def create_recommended(self, machine_code):
        recommendation = self.recommend(machine_code)

        if not recommendation.get("should_create_work_order"):
            return {
                "message": "No work order recommended"
            }

        description = "AI recommended maintenance action"

        if recommendation["reason"]:
            description = " | ".join(recommendation["reason"])

        return self.work_order_service.create_work_order(
            machine_code=machine_code,
            description=description,
            priority=recommendation["recommended_priority"]
        )
