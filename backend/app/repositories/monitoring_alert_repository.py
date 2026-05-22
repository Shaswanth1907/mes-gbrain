from app.models.monitoring_alert import MonitoringAlert


class MonitoringAlertRepository:
    def __init__(self, db):
        self.db = db

    def create(self, alert):
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get_open_alerts(self):
        return (
            self.db.query(MonitoringAlert)
            .filter(MonitoringAlert.status == "OPEN")
            .all()
        )

    def find_open_duplicate(self, machine_code, trigger_type):
        return (
            self.db.query(MonitoringAlert)
            .filter(
                MonitoringAlert.machine_code == machine_code,
                MonitoringAlert.trigger_type == trigger_type,
                MonitoringAlert.status == "OPEN"
            )
            .first()
        )
