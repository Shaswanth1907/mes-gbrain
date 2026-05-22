from app.repositories.technician_repository import TechnicianRepository
from app.graph.graph_query_service import GraphQueryService


class TechnicianSelectorService:
    def __init__(self, db):
        self.repo = TechnicianRepository(db)
        self.graph = GraphQueryService()

    def select_best(self, root_cause):
        skill_map = {
            "Bearing degradation": "Mechanical",
            "Belt wear": "Mechanical",
            "Motor failure": "Electrical"
        }

        required_skill = skill_map.get(root_cause)

        technicians = self.repo.get_available()

        if not technicians:
            return "Unassigned"

        workload = self.graph.technician_workload()

        workload_map = {
            item["technician"]: item["workload"]
            for item in workload["technician_workload"]
        }

        candidates = []

        for tech in technicians:
            if required_skill and tech.skill != required_skill:
                continue

            load = workload_map.get(tech.name, 0)

            candidates.append({
                "name": tech.name,
                "load": load
            })

        print("AVAILABLE TECHS:", technicians)
        print("WORKLOAD MAP:", workload_map)
        print("CANDIDATES:", candidates)

        if not candidates:
            return technicians[0].name

        candidates.sort(key=lambda x: x["load"])

        return candidates[0]["name"]
