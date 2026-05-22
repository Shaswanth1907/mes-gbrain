from app.graph.neo4j_client import neo4j_client
from app.graph.graph_repository import GraphRepository


class GraphSyncService:
    def __init__(self):
        self.repo = GraphRepository(neo4j_client)

    def sync_machine(self, machine):
        self.repo.merge_machine(machine)

    def sync_issue(self, issue, machine_code):
        try:
            print("SYNCING ISSUE TO NEO4J:", machine_code, issue.issue_ref)
            self.repo.merge_issue(issue, machine_code)
            print("NEO4J ISSUE SYNC SUCCESS")

        except Exception as e:
            import traceback
            print("NEO4J ERROR:")
            print(traceback.format_exc())

    def sync_work_order(self, work_order, machine_code):
        self.repo.merge_work_order(work_order, machine_code)

    def sync_maintenance(self, maintenance, machine_code):
        try:
            print(
                "SYNCING MAINTENANCE TO NEO4J:",
                machine_code,
                maintenance.id
            )

            self.repo.merge_maintenance(
                maintenance,
                machine_code
            )

            print("NEO4J MAINTENANCE SYNC SUCCESS")

        except Exception as e:
            import traceback
            print(traceback.format_exc())


graph_sync = GraphSyncService()
