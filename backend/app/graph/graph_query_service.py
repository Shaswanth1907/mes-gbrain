from app.graph.neo4j_client import neo4j_client


class GraphQueryService:
    def __init__(self):
        self.client = neo4j_client

    def technician_workload(self):
        query = """
        MATCH (t:Technician)<-[:ASSIGNED_TO]-(w:WorkOrder)
        RETURN t.name AS technician, count(w) AS workload
        ORDER BY workload DESC
        """

        with self.client.session() as session:
            result = session.run(query)

            rows = []
            for r in result:
                rows.append({
                    "technician": r["technician"],
                    "workload": r["workload"]
                })

            return {
                "technician_workload": rows
            }

    def machines_handled_by_technician(self, technician_name):
        query = """
        MATCH (m:Machine)-[:UNDERWENT]->(:Maintenance)-[:HANDLED_BY]->(t:Technician {name:$name})
        RETURN DISTINCT m.machine_code AS machine
        """

        with self.client.session() as session:
            result = session.run(query, name=technician_name)

            machines = [r["machine"] for r in result]

            return {
                "technician": technician_name,
                "machines": machines
            }

    def machine_dependency_view(self, machine_code):
        query = """
        MATCH (m:Machine {machine_code:$machine_code})-[r]->(n)
        RETURN type(r) AS relation, labels(n) AS labels, n
        """

        with self.client.session() as session:
            result = session.run(query, machine_code=machine_code)

            rows = []
            for r in result:
                rows.append({
                    "relation": r["relation"],
                    "target_type": r["labels"]
                })

            return {
                "machine_code": machine_code,
                "dependencies": rows
            }

    def impact_analysis(self, machine_code):
        query = """
        MATCH (m:Machine {machine_code:$machine_code})

        OPTIONAL MATCH (m)-[:HAS_ISSUE]->(i:Issue)
        OPTIONAL MATCH (m)-[:HAS_WORK_ORDER]->(w:WorkOrder)
        OPTIONAL MATCH (m)-[:UNDERWENT]->(mt:Maintenance)-[:HANDLED_BY]->(t:Technician)

        RETURN
            count(DISTINCT i) AS issues,
            count(DISTINCT w) AS work_orders,
            count(DISTINCT mt) AS maintenance,
            collect(DISTINCT t.name) AS technicians
        """

        with self.client.session() as session:
            result = session.run(
                query,
                machine_code=machine_code
            )

            row = result.single()

            if not row:
                return {
                    "message": f"Machine {machine_code} not found in graph"
                }

            total = (
                row["issues"] +
                row["work_orders"] +
                row["maintenance"]
            )

            risk = "LOW"

            if total >= 5:
                risk = "HIGH"
            elif total >= 2:
                risk = "MEDIUM"

            return {
                "machine_code": machine_code,
                "impacts": {
                    "open_issues": row["issues"],
                    "work_orders": row["work_orders"],
                    "maintenance_records": row["maintenance"],
                    "technicians": row["technicians"]
                },
                "risk_level": risk,
                "recommendation":
                    "Immediate intervention recommended"
                    if risk != "LOW"
                    else "Monitor machine"
            }

    def graph_explainability(self, machine_code):
        query = """
        MATCH (m:Machine {machine_code:$machine_code})

        OPTIONAL MATCH (m)-[:HAS_ISSUE]->(i:Issue)
        OPTIONAL MATCH (m)-[:HAS_WORK_ORDER]->(w:WorkOrder)
        OPTIONAL MATCH (m)-[:UNDERWENT]->(mt:Maintenance)-[:HANDLED_BY]->(t:Technician)

        RETURN
            count(DISTINCT i) AS issues,
            count(DISTINCT w) AS work_orders,
            count(DISTINCT mt) AS maintenance,
            collect(DISTINCT t.name) AS technicians
        """

        with self.client.session() as session:
            result = session.run(query, machine_code=machine_code)
            row = result.single()

            if not row:
                return {
                    "message": f"Machine {machine_code} not found"
                }

            evidence = []

            if row["issues"]:
                evidence.append(
                    f"Machine {machine_code} -> HAS_ISSUE -> {row['issues']} unresolved issue(s)"
                )

            if row["work_orders"]:
                evidence.append(
                    f"Machine {machine_code} -> HAS_WORK_ORDER -> {row['work_orders']} active work order(s)"
                )

            if row["maintenance"]:
                evidence.append(
                    f"Machine {machine_code} -> UNDERWENT -> {row['maintenance']} maintenance event(s)"
                )

            techs = [t for t in row["technicians"] if t]

            if techs:
                evidence.append(
                    f"Technician involvement detected: {', '.join(set(techs))}"
                )

            total = row["issues"] + row["work_orders"] + row["maintenance"]

            risk = "LOW"
            if total >= 5:
                risk = "HIGH"
            elif total >= 2:
                risk = "MEDIUM"

            return {
                "machine_code": machine_code,
                "risk_level": risk,
                "evidence_path": evidence,
                "root_reason": "Compounding unresolved operational dependencies"
            }

    def failure_propagation(self, machine_code):
        query = """
        MATCH (m:Machine {machine_code:$machine_code})

        OPTIONAL MATCH (m)-[:HAS_ISSUE]->(i:Issue)
        OPTIONAL MATCH (m)-[:HAS_WORK_ORDER]->(w:WorkOrder)-[:ASSIGNED_TO]->(tw:Technician)
        OPTIONAL MATCH (m)-[:UNDERWENT]->(mt:Maintenance)-[:HANDLED_BY]->(tm:Technician)

        RETURN
            count(DISTINCT i) AS issues,
            count(DISTINCT w) AS work_orders,
            count(DISTINCT mt) AS maintenance_records,
            collect(DISTINCT tw.name) + collect(DISTINCT tm.name) AS technicians
        """

        with self.client.session() as session:
            result = session.run(query, machine_code=machine_code)

            row = result.single()

            if not row:
                return {
                    "message": f"Machine {machine_code} not found"
                }

            issues = row["issues"] or 0
            work_orders = row["work_orders"] or 0
            maintenance_records = row["maintenance_records"] or 0

            technicians = [
                t for t in set(row["technicians"])
                if t
            ]

            cascade_effects = []
            score = 0

            if issues:
                cascade_effects.append(
                    f"{issues} open issue(s) may worsen"
                )
                score += issues

            if work_orders:
                cascade_effects.append(
                    f"{work_orders} active work order(s) may be delayed"
                )
                score += work_orders

            if maintenance_records:
                cascade_effects.append(
                    f"{maintenance_records} maintenance record(s) may require review"
                )
                score += maintenance_records

            if technicians:
                cascade_effects.append(
                    f"Technician workload may increase for: {', '.join(technicians)}"
                )
                score += len(technicians)

            if score >= 6:
                risk = "HIGH"
            elif score >= 3:
                risk = "MEDIUM"
            else:
                risk = "LOW"

            return {
                "machine_code": machine_code,
                "cascade_effects": cascade_effects,
                "affected_technicians": technicians,
                "estimated_operational_risk": risk
            }
