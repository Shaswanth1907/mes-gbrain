from app.services.root_cause_service import RootCauseService
from app.services.spare_impact_service import SpareImpactService
from app.services.technician_selector_service import TechnicianSelectorService
from app.graph.graph_query_service import GraphQueryService


class AutonomousMaintenancePlanner:
    def __init__(self, db):
        self.root_cause_service = RootCauseService(db)
        self.spare_service = SpareImpactService(db)
        self.tech_selector = TechnicianSelectorService(db)
        self.graph_service = GraphQueryService()

    def plan(self, machine_code):
        root = self.root_cause_service.analyze(machine_code)
        spare = self.spare_service.assess(machine_code)
        workload = self.graph_service.technician_workload()

        root_cause = root.get("root_cause", "Unknown")

        part_map = {
            "Bearing degradation": {
                "part": "BR-220",
                "action": "Replace BR-220 bearing immediately",
                "downtime": 45
            },
            "Belt wear": {
                "part": "BLT-101",
                "action": "Replace drive belt immediately",
                "downtime": 30
            },
            "Motor failure": {
                "part": "MTR-500",
                "action": "Replace motor assembly",
                "downtime": 90
            }
        }

        action_info = part_map.get(
            root_cause,
            {
                "part": "UNKNOWN",
                "action": "Inspect machine manually",
                "downtime": 60
            }
        )

        technician = self.tech_selector.select_best(root_cause)

        inventory_ready = spare.get("procurement_risk") != "HIGH"

        priority = "URGENT" if inventory_ready else "HIGH"

        execution_plan = [
            "Create urgent work order",
            f"Reserve {action_info['part']} spare part",
            f"Assign technician {technician}",
            "Schedule corrective maintenance immediately"
        ]

        return {
            "machine_code": machine_code,
            "risk_level": "HIGH",
            "root_cause": root_cause,
            "recommended_action": action_info["action"],
            "assigned_technician": technician,
            "inventory_ready": inventory_ready,
            "estimated_downtime_minutes": action_info["downtime"],
            "priority": priority,
            "execution_plan": execution_plan
        }
