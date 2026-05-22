import logging

from app.services.production_kpi_service import ProductionKPIService
from app.services.issue_service import IssueService
from app.services.maintenance_service import MaintenanceService
from app.services.work_order_service import WorkOrderService
from app.services.predictive_service import PredictiveService
from app.services.root_cause_service import RootCauseService

logger = logging.getLogger("mes_gbrain")


class ShiftSummaryService:
    def __init__(self, db):
        self.kpi_service = ProductionKPIService(db)
        self.issue_service = IssueService(db)
        self.maintenance_service = MaintenanceService(db)
        self.work_order_service = WorkOrderService(db)
        self.predictive_service = PredictiveService(db)
        self.root_cause_service = RootCauseService(db)

    def summarize_machine_shift(self, machine_code):
        try:
            kpi = self.kpi_service.get_machine_kpi(machine_code)
            issues = self.issue_service.get_open_issues(machine_code)
            maintenance = self.maintenance_service.get_history(machine_code)
            work_orders = self.work_order_service.get_open_work_orders(machine_code)
            risk = self.predictive_service.predict_failure_risk(machine_code)
            root_cause = self.root_cause_service.analyze(machine_code)

            open_issues = issues.get("open_issues", [])
            history = maintenance.get("history", [])
            open_work_orders = work_orders.get("open_work_orders", [])

            recommendation = "Machine is operating within acceptable limits."

            if risk.get("risk_level") == "HIGH":
                recommendation = "Immediate maintenance attention recommended."
            elif risk.get("risk_level") == "MEDIUM":
                recommendation = "Monitor machine closely and review open issues."
            elif root_cause.get("root_cause") != "Unknown":
                recommendation = root_cause.get("recommendation")

            return {
                "machine_code": machine_code,
                "shift_summary": {
                    "planned_minutes": kpi.get("planned_minutes"),
                    "runtime_minutes": kpi.get("runtime_minutes"),
                    "downtime_minutes": kpi.get("downtime_minutes"),
                    "availability_percent": kpi.get("availability_percent"),
                    "performance_percent": kpi.get("performance_percent"),
                    "quality_percent": kpi.get("quality_percent"),
                    "oee_percent": kpi.get("oee_percent"),
                    "total_count": kpi.get("total_count"),
                    "good_count": kpi.get("good_count"),
                    "reject_count": kpi.get("reject_count"),
                    "open_issues_count": len(open_issues),
                    "maintenance_records_count": len(history),
                    "open_work_orders_count": len(open_work_orders),
                    "risk_level": risk.get("risk_level"),
                    "root_cause": root_cause.get("root_cause")
                },
                "open_issues": open_issues,
                "open_work_orders": open_work_orders,
                "recommendation": recommendation
            }

        except Exception as e:
            logger.error(f"Shift summary failed: {str(e)}")
            return {
                "message": "Failed to generate shift summary"
            }
