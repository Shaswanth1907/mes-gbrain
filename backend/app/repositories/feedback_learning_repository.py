from app.models.feedback_learning import FeedbackLearning


class FeedbackLearningRepository:
    def __init__(self, db):
        self.db = db

    def create(self, data):
        record = FeedbackLearning(**data)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_by_machine(self, machine_code):
        return (
            self.db.query(FeedbackLearning)
            .filter(FeedbackLearning.machine_code == machine_code)
            .all()
        )

    def get_all(self):
        return self.db.query(FeedbackLearning).all()
