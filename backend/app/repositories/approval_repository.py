from app.models.approval import Approval


class ApprovalRepository:
    def __init__(self, db):
        self.db = db

    def create(self, approval):
        self.db.add(approval)
        self.db.commit()
        self.db.refresh(approval)
        return approval

    def get_by_ref(self, approval_ref):
        return (
            self.db.query(Approval)
            .filter(Approval.approval_ref == approval_ref)
            .first()
        )

    def approve(self, approval):
        approval.status = "APPROVED"
        self.db.commit()
        self.db.refresh(approval)
        return approval
