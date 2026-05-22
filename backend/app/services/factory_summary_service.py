import logging

from app.repositories.machine_repository import MachineRepository
from app.services.shift_summary_service import ShiftSummaryService

logger = logging.getLogger("mes_gbrain")


class FactorySummaryService:
    def __init__(self, db):
        self.machine_repo = MachineRepository(db)
        self.shift_service = ShiftSummaryService(db)

    def summarize_factory(self):
        try:
            machines = self.machine_repo.get_all()

            if not machines:
                return {
                    "message": "No machines found"
                }

            total_runtime = 0
            total_downtime = 0
            total_issues = 0
            total_work_orders = 0
            total_rejects = 0
            oee_values = []
            machine_summaries = []

            for machine in machines:
                print("MACHINE:", machine.machine_code)
                summary = self.shift_service.summarize_machine_shift(
                    machine.machine_code
                )
                print(summary)

                shift = summary.get("shift_summary", {})

                total_runtime += shift.get("runtime_minutes", 0) or 0
                total_downtime += shift.get("downtime_minutes", 0) or 0
                total_issues += shift.get("open_issues_count", 0) or 0
                total_work_orders += shift.get(
                    "open_work_orders_count",
                    0
                ) or 0
                total_rejects += shift.get("reject_count", 0) or 0

                if shift.get("oee_percent") is not None:
                    oee_values.append(shift["oee_percent"])

                machine_summaries.append({
                    "machine_code": machine.machine_code,
                    "status": machine.status,
                    "risk_level": shift.get("risk_level"),
                    "oee_percent": shift.get("oee_percent")
                })

            avg_oee = round(
                sum(oee_values) / len(oee_values),
                2
            ) if oee_values else 0

            recommendation = "Factory operating normally"

            if avg_oee < 70:
                recommendation = (
                    "Factory OEE below target. Review bottlenecks."
                )

            if total_issues > 5:
                recommendation = (
                    "High issue volume detected. Immediate review recommended."
                )

            return {
                "factory_summary": {
                    "total_machines": len(machines),
                    "total_runtime_minutes": total_runtime,
                    "total_downtime_minutes": total_downtime,
                    "average_oee_percent": avg_oee,
                    "total_open_issues": total_issues,
                    "total_open_work_orders": total_work_orders,
                    "total_reject_count": total_rejects
                },
                "machine_summaries": machine_summaries,
                "recommendation": recommendation
            }

        except Exception as e:
            logger.error(f"Factory summary failed: {str(e)}")
            return {
                "message": "Factory summary failed"
            }
