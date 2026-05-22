from app.repositories.issue_repository import IssueRepository
from app.repositories.machine_repository import MachineRepository
from app.repositories.spare_part_repository import SparePartRepository
from app.repositories.work_order_repository import WorkOrderRepository
from app.graph.graph_query_service import GraphQueryService


class ToolExecutor:
    def __init__(self, db):
        self.db = db
        self.machine_repo = MachineRepository(db)
        self.issue_repo = IssueRepository(db)
        self.work_order_repo = WorkOrderRepository(db)
        self.spare_repo = SparePartRepository(db)
        self.graph_service = GraphQueryService()
    def execute(self, plan: dict):
        tool = plan.get("tool")
        action = plan.get("action")
        params = plan.get("params", {})

        if tool == "machine_query":
            return self._machine_query(action)

        if tool == "issue_query":
            return self._issue_query(action)

        if tool == "work_order_query":
            return self._work_order_query(action)

        if tool == "inventory_query":
            return self._inventory_query(action)

        if tool == "graph_query":
            return self._graph_query(action, params)

        return {
            "message": "I could not understand the operational query yet."
        }

    def _machine_query(self, action):
        if action == "list_running_machines":
            machines = self.machine_repo.get_running()

            return {
                "machines": [
                    {
                        "machine_code": m.machine_code,
                        "name": m.name,
                        "location": m.location,
                        "status": m.status
                    }
                    for m in machines
                ]
            }

        if action == "list_all_machines":
            machines = self.machine_repo.get_all()

            return {
                "machines": [
                    {
                        "machine_code": m.machine_code,
                        "name": m.name,
                        "location": m.location,
                        "status": m.status
                    }
                    for m in machines
                ]
            }

        return {"message": "Machine query action not supported"}

    def _issue_query(self, action):
        if action == "list_open_issues":
            issues = self.issue_repo.get_open()

            return {
                "open_issues": [
                    {
                        "issue_ref": i.issue_ref,
                        "machine_id": i.machine_id,
                        "title": i.title,
                        "severity": i.severity,
                        "status": i.status
                    }
                    for i in issues
                ]
            }

        return {"message": "Issue query action not supported"}

    def _work_order_query(self, action):
        if action == "list_open_work_orders":
            work_orders = self.work_order_repo.get_open()

            return {
                "open_work_orders": [
                    {
                        "work_order_ref": w.work_order_ref,
                        "machine_id": w.machine_id,
                        "title": w.title,
                        "priority": w.priority,
                        "status": w.status,
                        "assigned_to": w.assigned_to
                    }
                    for w in work_orders
                ]
            }

        return {"message": "Work order query action not supported"}

    def _inventory_query(self, action):
        if action == "list_low_stock_parts":
            parts = self.spare_repo.get_low_stock()

            return {
                "low_stock_parts": [
                    {
                        "part_code": p.part_code,
                        "part_name": p.part_name,
                        "quantity": p.quantity,
                        "reorder_level": p.reorder_level
                    }
                    for p in parts
                ]
            }

        return {"message": "Inventory query action not supported"}

    def _graph_query(self, action, params):
        if action == "technician_workload":
            return self.graph_service.technician_workload()

        if action == "machine_dependency":
            return self.graph_service.machine_dependency_view(
                params.get("machine_code")
            )

        return {"message": "Graph query action not supported"}
