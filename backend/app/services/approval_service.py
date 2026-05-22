import uuid
from datetime import datetime

from app.models.approval import Approval
from app.repositories.approval_repository import ApprovalRepository
from app.services.autonomous_maintenance_planner import AutonomousMaintenancePlanner
from app.services.execute_corrective_plan_service import ExecuteCorrectivePlanService


class ApprovalService:
    def __init__(self, db):
        self.db = db
        self.repo = ApprovalRepository(db)
        self.planner = AutonomousMaintenancePlanner(db)
        self.executor = ExecuteCorrectivePlanService(db)

    def request_approval(self, machine_code):
        plan = self.planner.plan(machine_code)

        approval = Approval(
            approval_ref=f"APR-{uuid.uuid4().hex[:8]}",
            machine_code=machine_code,
            status="PENDING_APPROVAL",
            plan_json=plan
        )

        self.repo.create(approval)

        return {
            "approval_id": approval.approval_ref,
            "machine_code": machine_code,
            "status": approval.status,
            "proposed_actions": plan["execution_plan"]
        }

    def approve(self, approval_ref):
        approval = self.repo.get_by_ref(approval_ref)

        if not approval:
            return {
                "message": "Approval request not found"
            }

        if approval.status == "APPROVED":
            return {
                "message": "Already approved"
            }

        approval.status = "APPROVED"
        approval.approved_at = datetime.utcnow()
        self.db.commit()

        return self.executor.execute(
            approval.machine_code
        )
