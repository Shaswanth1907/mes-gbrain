from sqlalchemy.orm import Session
from app.models.issue import Issue


class IssueRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(Issue).all()

    def get_by_machine_id(self, machine_id: int):
        return self.db.query(Issue).filter(
            Issue.machine_id == machine_id
        ).all()

    def get_by_machine(self, machine_id):
        return (
            self.db.query(Issue)
            .filter(Issue.machine_id == machine_id)
            .all()
        )

    def get_open_by_machine(self, machine_id: int):
        return (
            self.db.query(Issue)
            .filter(
                Issue.machine_id == machine_id,
                Issue.status == "OPEN"
            )
            .all()
        )

    def get_open(self):
        return (
            self.db.query(Issue)
            .filter(
                Issue.status.in_([
                    "OPEN",
                    "open",
                    "ACTIVE",
                    "active",
                    "PENDING",
                    "pending"
                ])
            )
            .all()
        )

    def count_open_by_machine(self, machine_id):
        return (
            self.db.query(Issue)
            .filter(
                Issue.machine_id == machine_id,
                Issue.status == "OPEN"
            )
            .count()
        )

    def get_by_ref(self, issue_ref: str):
        return (
            self.db.query(Issue)
            .filter(Issue.issue_ref == issue_ref)
            .first()
        )

    def close_issue(self, issue_ref: str):
        issue = self.get_by_ref(issue_ref)

        if not issue:
            return None

        issue.status = "CLOSED"

        self.db.commit()
        self.db.refresh(issue)

        return issue

    def escalate(self, issue, escalated_to):
        issue.status = "ESCALATED"
        issue.escalated_to = escalated_to
        self.db.commit()
        self.db.refresh(issue)
        return issue

    def create(
        self,
        issue_ref,
        machine_id,
        title,
        description,
        severity,
        status="OPEN"
    ):
        issue = Issue(
            issue_ref=issue_ref,
            machine_id=machine_id,
            title=title,
            description=description,
            severity=severity,
            status=status
        )

        self.db.add(issue)
        self.db.commit()
        self.db.refresh(issue)

        return issue
