class GraphRepository:
    def __init__(self, client):
        self.client = client

    def merge_machine(self, machine):
        query = """
        MERGE (m:Machine {machine_code: $machine_code})
        SET
            m.machine_ref = $machine_ref,
            m.name = $name,
            m.location = $location,
            m.status = $status
        """

        with self.client.session() as session:
            session.run(
                query,
                machine_code=machine.machine_code,
                machine_ref=machine.machine_ref,
                name=machine.name,
                location=machine.location,
                status=machine.status
            )

    def merge_issue(self, issue, machine_code):
        print("MERGING ISSUE NODE")
        query = """
        MERGE (m:Machine {machine_code: $machine_code})

        MERGE (i:Issue {issue_ref: $issue_ref})
        SET
            i.title = $title,
            i.severity = $severity,
            i.status = $status

        MERGE (m)-[:HAS_ISSUE]->(i)
        """

        with self.client.session() as session:
            result = session.run(
                query,
                machine_code=machine_code,
                issue_ref=issue.issue_ref,
                title=issue.title,
                severity=issue.severity,
                status=issue.status
            )
            result.consume()

    def merge_work_order(self, wo, machine_code):
        query = """
        MERGE (m:Machine {machine_code: $machine_code})

        MERGE (w:WorkOrder {work_order_ref: $work_order_ref})
        SET
            w.title = $title,
            w.priority = $priority,
            w.status = $status,
            w.assigned_to = $assigned_to

        MERGE (m)-[:HAS_WORK_ORDER]->(w)

        MERGE (t:Technician {name: $assigned_to})
        MERGE (w)-[:ASSIGNED_TO]->(t)
        """

        with self.client.session() as session:
            result = session.run(
                query,
                machine_code=machine_code,
                work_order_ref=wo.work_order_ref,
                title=wo.title,
                priority=wo.priority,
                status=wo.status,
                assigned_to=wo.assigned_to or "Unassigned"
            )
            result.consume()

    def merge_maintenance(self, maintenance, machine_code):
        query = """
        MERGE (m:Machine {machine_code: $machine_code})

        MERGE (mt:Maintenance {maintenance_id: $maintenance_id})
        SET
            mt.activity = $activity,
            mt.status = $status,
            mt.technician = $technician,
            mt.maintenance_date = $maintenance_date

        MERGE (m)-[:UNDERWENT]->(mt)

        MERGE (t:Technician {name: $technician})
        MERGE (mt)-[:HANDLED_BY]->(t)
        """

        with self.client.session() as session:
            result = session.run(
                query,
                machine_code=machine_code,
                maintenance_id=maintenance.id,
                activity=maintenance.activity,
                status=maintenance.status,
                technician=maintenance.technician or "Unassigned",
                maintenance_date=str(maintenance.maintenance_date)
            )
            result.consume()
