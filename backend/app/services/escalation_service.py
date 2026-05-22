import logging

from app.repositories.issue_repository import IssueRepository
from app.repositories.work_order_repository import WorkOrderRepository

logger = logging.getLogger("mes_gbrain")


class EscalationService:
    def __init__(self, db):
        self.issue_repo = IssueRepository(db)
        self.work_order_repo = WorkOrderRepository(db)

    def escalate_issue(self, issue_ref, escalated_to):
        try:
            issue = self.issue_repo.get_by_ref(issue_ref)

            if not issue:
                return {
                    "message": f"Issue {issue_ref} not found"
                }

            issue = self.issue_repo.escalate(issue, escalated_to)

            return {
                "message": "Issue escalated successfully",
                "issue_ref": issue_ref,
                "status": issue.status,
                "escalated_to": escalated_to
            }

        except Exception as e:
            logger.error(str(e))
            return {
                "message": "Issue escalation failed"
            }

    def escalate_work_order(self, work_order_ref, escalated_to):
        try:
            wo = self.work_order_repo.get_by_ref(work_order_ref)

            if not wo:
                return {
                    "message": f"Work order {work_order_ref} not found"
                }

            wo = self.work_order_repo.escalate(wo, escalated_to)

            return {
                "message": "Work order escalated successfully",
                "work_order_ref": work_order_ref,
                "status": wo.status,
                "escalated_to": escalated_to
            }

        except Exception as e:
            logger.error(str(e))
            return {
                "message": "Work order escalation failed"
            }
