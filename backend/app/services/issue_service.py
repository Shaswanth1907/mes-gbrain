from app.repositories.issue_repository import IssueRepository
from app.repositories.machine_repository import MachineRepository
from app.graph.graph_sync_service import graph_sync
import uuid
import logging

logger = logging.getLogger("mes_gbrain")


class IssueService:
    def __init__(self, db):
        self.issue_repo = IssueRepository(db)
        self.machine_repo = MachineRepository(db)

    def create_issue(self, machine_code, description, severity="MEDIUM"):
        try:
            logger.info(f"Creating issue | machine_code={machine_code}")

            machine = self.machine_repo.get_by_code(machine_code)

            if not machine:
                return {
                    "message": f"Machine {machine_code} not found"
                }

            issue = self.issue_repo.create(
                issue_ref=str(uuid.uuid4())[:8],
                machine_id=machine.id,
                title="AI Generated Issue",
                description=description,
                severity=severity,
                status="OPEN"
            )

            graph_sync.sync_issue(issue, machine.machine_code)

            return {
                "message": "Issue created successfully",
                "issue_id": issue.id,
                "issue_ref": issue.issue_ref,
                "machine_code": machine_code
            }

        except Exception as e:
            logger.error(f"Create issue failed: {str(e)}")
            return {"message": "Failed to create issue"}

    def get_open_issues(self, machine_code):
        try:
            logger.info(f"Fetching open issues | machine_code={machine_code}")

            machine = self.machine_repo.get_by_code(machine_code)

            if not machine:
                return {
                    "message": f"Machine {machine_code} not found"
                }

            issues = self.issue_repo.get_open_by_machine(machine.id)

            return {
                "machine_code": machine_code,
                "open_issues": [
                    {
                        "issue_ref": issue.issue_ref,
                        "title": issue.title,
                        "severity": issue.severity,
                        "status": issue.status
                    }
                    for issue in issues
                ]
            }

        except Exception as e:
            logger.error(f"Open issue fetch failed: {str(e)}")
            return {"message": "Failed to fetch open issues"}

    def close_issue(self, issue_ref):
        try:
            logger.info(f"Closing issue | issue_ref={issue_ref}")

            issue = self.issue_repo.close_issue(issue_ref)

            if not issue:
                return {
                    "message": f"Issue {issue_ref} not found"
                }

            return {
                "message": "Issue closed successfully",
                "issue_ref": issue.issue_ref,
                "status": issue.status
            }

        except Exception as e:
            logger.error(f"Close issue failed: {str(e)}")
            return {"message": "Failed to close issue"}
