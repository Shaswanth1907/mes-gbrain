import uuid

from app.models.monitoring_alert import MonitoringAlert
from app.repositories.machine_repository import MachineRepository
from app.repositories.monitoring_alert_repository import MonitoringAlertRepository
from app.services.approval_service import ApprovalService
from app.services.notification_service import NotificationService
from app.services.production_kpi_service import ProductionKPIService
from app.services.anomaly_detection_service import AnomalyDetectionService
from app.services.predictive_service import PredictiveService
from app.services.spare_part_service import SparePartService


class MonitoringService:
    def __init__(self, db):
        self.db = db
        self.machine_repo = MachineRepository(db)
        self.alert_repo = MonitoringAlertRepository(db)
        self.approval_service = ApprovalService(db)
        self.notification_service = NotificationService()
        self.kpi_service = ProductionKPIService(db)
        self.anomaly_service = AnomalyDetectionService(db)
        self.predictive_service = PredictiveService(db)
        self.spare_service = SparePartService(db)

    def run_check(self):
        machines = self.machine_repo.get_all()

        alerts_created = []

        for machine in machines:
            machine_code = machine.machine_code

            kpi = self.kpi_service.get_machine_kpi(machine_code)
            anomaly = self.anomaly_service.detect(machine_code)
            risk = self.predictive_service.predict_failure_risk(machine_code)

            if kpi.get("oee_percent") is not None and kpi.get("oee_percent") < 70:
                alerts_created.append(
                    self._create_alert(
                        machine_code=machine_code,
                        trigger_type="OEE_BELOW_TARGET",
                        severity="HIGH",
                        message=f"OEE is below target at {kpi.get('oee_percent')}%",
                        recommendation="Review downtime, active work orders, and corrective maintenance plan."
                    )
                )

            if (kpi.get("downtime_minutes") or 0) > 45:
                alerts_created.append(
                    self._create_alert(
                        machine_code=machine_code,
                        trigger_type="HIGH_DOWNTIME",
                        severity="MEDIUM",
                        message=f"Downtime is high at {kpi.get('downtime_minutes')} minutes.",
                        recommendation="Prioritize maintenance and investigate stoppage reasons."
                    )
                )

            if (kpi.get("reject_count") or 0) > 30:
                alerts_created.append(
                    self._create_alert(
                        machine_code=machine_code,
                        trigger_type="HIGH_REJECT_COUNT",
                        severity="MEDIUM",
                        message=f"Reject count is high at {kpi.get('reject_count')}.",
                        recommendation="Review quality process and operator checks."
                    )
                )

            if anomaly.get("anomaly_detected"):
                alerts_created.append(
                    self._create_alert(
                        machine_code=machine_code,
                        trigger_type="ANOMALY_DETECTED",
                        severity=anomaly.get("severity", "MEDIUM"),
                        message=", ".join(anomaly.get("anomalies", [])),
                        recommendation=anomaly.get("recommendation", "Investigate anomaly.")
                    )
                )

            if risk.get("risk_level") in ["HIGH", "MEDIUM"]:
                alerts_created.append(
                    self._create_alert(
                        machine_code=machine_code,
                        trigger_type="PREDICTIVE_RISK",
                        severity=risk.get("risk_level"),
                        message=f"Predictive risk detected: {risk.get('risk_level')}",
                        recommendation="Run corrective action planning."
                    )
                )

        return {
            "message": "Monitoring check completed",
            "alerts_created": [
                {
                    "alert_ref": alert.alert_ref,
                    "machine_code": alert.machine_code,
                    "trigger_type": alert.trigger_type,
                    "severity": alert.severity,
                    "message": alert.message,
                    "recommendation": alert.recommendation,
                    "status": alert.status
                }
                for alert in alerts_created
            ]
        }

    def _create_alert(self, machine_code, trigger_type, severity, message, recommendation):
        existing = self.alert_repo.find_open_duplicate(
            machine_code=machine_code,
            trigger_type=trigger_type
        )

        if existing:
            if severity == "HIGH" and "Approval created:" not in (existing.recommendation or ""):
                approval = self._auto_create_approval(machine_code)

                self.notification_service.send_email(
                    recipients=["shaswanthbaskaran@gmail.com"],
                    subject=f"HIGH ALERT: {machine_code}",
                    body=(
                        f"Machine: {machine_code}\n"
                        f"Trigger: {trigger_type}\n"
                        f"Severity: {severity}\n"
                        f"Approval: {approval.get('approval_id')}"
                    )
                )

                existing.recommendation = (
                    f"{existing.recommendation} Approval created: {approval.get('approval_id')}"
                )

                self.db.commit()
                self.db.refresh(existing)

            return existing

        alert = MonitoringAlert(
            alert_ref=f"ALT-{uuid.uuid4().hex[:8]}",
            machine_code=machine_code,
            trigger_type=trigger_type,
            severity=severity,
            message=message,
            recommendation=recommendation,
            status="OPEN"
        )

        created_alert = self.alert_repo.create(alert)

        if severity == "HIGH":
            approval = self._auto_create_approval(machine_code)

            self.notification_service.send_email(
                recipients=["shaswanthbaskaran@gmail.com"],
                subject=f"HIGH ALERT: {machine_code}",
                body=(
                    f"Machine: {machine_code}\n"
                    f"Trigger: {trigger_type}\n"
                    f"Severity: {severity}\n"
                    f"Approval: {approval.get('approval_id')}"
                )
            )

            created_alert.recommendation = (
                f"{recommendation} Approval created: {approval.get('approval_id')}"
            )

            self.db.commit()
            self.db.refresh(created_alert)

        return created_alert

    def _auto_create_approval(self, machine_code):
        return self.approval_service.request_approval(machine_code)

    def get_open_alerts(self):
        alerts = self.alert_repo.get_open_alerts()

        return {
            "open_alerts": [
                {
                    "alert_ref": a.alert_ref,
                    "machine_code": a.machine_code,
                    "trigger_type": a.trigger_type,
                    "severity": a.severity,
                    "message": a.message,
                    "recommendation": a.recommendation,
                    "status": a.status
                }
                for a in alerts
            ]
        }
