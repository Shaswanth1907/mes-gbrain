import json
import re

from app.graph.neo4j_client import neo4j_client


class Neo4jAgent:
    def __init__(self, llm_service):
        self.client = neo4j_client
        self.llm_service = llm_service

    def answer(self, question: str):
        cypher = self._generate_cypher(question)
        cypher = self._validate_cypher(cypher)

        with self.client.session() as session:
            result = session.run(cypher)
            rows = []

            for row in result:
                rows.append(self._serialize_record(row))

        return self._format_response(question, rows)

    def _generate_cypher(self, question: str) -> str:
        prompt = f"""
You are a Neo4j Cypher generator for a Manufacturing Execution System graph.

Generate ONLY a READ-ONLY Cypher query.
Do not explain.
Do not use CREATE, MERGE, SET, DELETE, REMOVE, DROP.

Available graph model:

(:Machine {{machine_code, name, status, location}})
(:Issue {{issue_ref, title, severity, status}})
(:WorkOrder {{work_order_ref, title, priority, status, assigned_to}})
(:Maintenance {{maintenance_id, activity, status, technician, maintenance_date}})
(:Technician {{name}})
(:SparePart {{part_code, part_name, quantity, reorder_level}})

Relationships:
(:Machine)-[:HAS_ISSUE]->(:Issue)
(:Machine)-[:HAS_WORK_ORDER]->(:WorkOrder)
(:Machine)-[:UNDERWENT]->(:Maintenance)
(:WorkOrder)-[:ASSIGNED_TO]->(:Technician)
(:Maintenance)-[:HANDLED_BY]->(:Technician)
(:Machine)-[:USES_PART]->(:SparePart)

Rules:
- Only MATCH / OPTIONAL MATCH / RETURN queries.
- Always LIMIT 50.
- Return useful properties, not full huge paths unless asked for graph/path.

Question:
{question}

Cypher:
"""

        response = self.llm_service.generate(prompt)
        return self._extract_cypher(response)

    def _extract_cypher(self, response: str) -> str:
        response = response.strip()
        response = response.replace("```cypher", "").replace("```", "").strip()

        match = re.search(
            r"(MATCH[\s\S]+|OPTIONAL MATCH[\s\S]+)",
            response,
            re.IGNORECASE
        )

        if not match:
            raise ValueError("No read Cypher query found")

        return match.group(1).strip().rstrip(";")

    def _validate_cypher(self, cypher: str) -> str:
        lowered = cypher.lower()

        allowed_start = (
            lowered.startswith("match")
            or lowered.startswith("optional match")
        )

        if not allowed_start:
            raise ValueError("Only MATCH queries are allowed")

        forbidden = [
            "create",
            "merge",
            "set",
            "delete",
            "remove",
            "drop",
            "detach",
            "call dbms",
            "load csv"
        ]

        for word in forbidden:
            if word in lowered:
                raise ValueError(f"Forbidden Cypher keyword detected: {word}")

        if "limit" not in lowered:
            cypher = cypher.rstrip(";") + " LIMIT 50"

        return cypher

    def _serialize_record(self, record):
        output = {}

        for key in record.keys():
            value = record[key]

            if hasattr(value, "items"):
                output[key] = dict(value)
            elif isinstance(value, list):
                output[key] = [
                    dict(v) if hasattr(v, "items") else str(v)
                    for v in value
                ]
            else:
                output[key] = value

        return output

    def _format_response(self, question, rows):
        prompt = f"""
You are GBrain, autonomous manufacturing intelligence assistant.

User Question:
{question}

Retrieved Graph Data:
{json.dumps(rows, default=str)}

Return ONLY valid JSON.

Examples:

{{
  "affected_machines": [
    "M-101",
    "M-103"
  ]
}}

Rules:
- ONLY valid JSON
- NO markdown
- NO explanation
- NEVER mention Neo4j
"""

        response = self.llm_service.generate(prompt)

        try:
            cleaned = response.strip()
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

            parsed = json.loads(cleaned)

            return {
                "answer": parsed
            }
        except Exception:
            return {
                "answer": rows
            }
