from app.services.production_kpi_service import ProductionKPIService
from app.services.shift_summary_service import ShiftSummaryService
from app.services.failure_advisor_service import FailureAdvisorService
from app.services.anomaly_detection_service import AnomalyDetectionService


class ProductionOptimizationService:
    def __init__(self, db):
        self.kpi_service = ProductionKPIService(db)
        self.shift_service = ShiftSummaryService(db)
        self.failure_service = FailureAdvisorService(db)
        self.anomaly_service = AnomalyDetectionService(db)

    def optimize_machine(self, machine_code):
        kpi = self.kpi_service.get_machine_kpi(machine_code)
        shift = self.shift_service.summarize_machine_shift(machine_code)
        failure = self.failure_service.advise(machine_code)
        anomaly = self.anomaly_service.detect(machine_code)

        recommendations = []

        oee = kpi.get("oee_percent", 0) or 0
        downtime = kpi.get("downtime_minutes", 0) or 0
        reject_count = kpi.get("reject_count", 0) or 0
        availability = kpi.get("availability_percent", 0) or 0
        performance = kpi.get("performance_percent", 0) or 0
        quality = kpi.get("quality_percent", 0) or 0

        if oee < 70:
            recommendations.append("Improve OEE by reducing downtime and resolving active work orders.")

        if downtime > 45:
            recommendations.append("Reduce downtime by prioritizing corrective maintenance.")

        if reject_count > 30:
            recommendations.append("Review quality issues because reject count is above target.")

        if availability < 90:
            recommendations.append("Increase availability by preventing unplanned stoppages.")

        if performance < 85:
            recommendations.append("Improve performance by checking cycle time losses and machine speed constraints.")

        if quality < 97:
            recommendations.append("Improve quality by reviewing defect causes and operator process checks.")

        if anomaly.get("anomaly_detected"):
            recommendations.append("Investigate detected anomalies before the next production run.")

        for item in failure.get("recommendations", []):
            if item not in recommendations:
                recommendations.append(item)

        if not recommendations:
            recommendations.append("Production is stable. Continue monitoring current performance.")

        return {
            "machine_code": machine_code,
            "current_oee": oee,
            "availability_percent": availability,
            "performance_percent": performance,
            "quality_percent": quality,
            "downtime_minutes": downtime,
            "reject_count": reject_count,
            "optimization_focus": self._focus_area(availability, performance, quality),
            "recommendations": recommendations
        }

    def _focus_area(self, availability, performance, quality):
        values = {
            "availability": availability,
            "performance": performance,
            "quality": quality
        }

        weakest = min(values, key=values.get)

        if weakest == "availability":
            return "Reduce downtime and improve machine availability"

        if weakest == "performance":
            return "Improve cycle time and production speed"

        return "Reduce rejects and improve production quality"
