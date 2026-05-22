from app.models.technician import Technician


class TechnicianRepository:
    def __init__(self, db):
        self.db = db

    def get_available(self):
        return (
            self.db.query(Technician)
            .filter(Technician.status == "AVAILABLE")
            .all()
        )
