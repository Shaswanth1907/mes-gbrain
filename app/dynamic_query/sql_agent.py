import json
import re

import sqlparse
from sqlalchemy import text


class SQLAgent:
    def __init__(self, db, llm_service):
        self.db = db
        self.llm_service = llm_service

    def answer(self, question: str):
        sql = self._generate_sql(question)
        sql = self._validate_sql(sql)

        try:
            result = self.db.execute(text(sql))
            rows = result.mappings().all()
        except Exception as e:
            repaired_sql = self._repair_sql(question, sql, str(e))
            repaired_sql = self._validate_sql(repaired_sql)

            result = self.db.execute(text(repaired_sql))
            rows = result.mappings().all()

        return self._format_response(question, rows)

    def _generate_sql(self, question: str) -> str:
        prompt = f"""
You are a PostgreSQL SQL generator for a Manufacturing Execution System.

Generate ONLY a SELECT SQL query.
Do not explain.
Do not use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE.

Available tables:

machines(
    id,
    machine_ref,
    machine_code,
    name,
    location,
    status
)

issues(
    id,
    issue_ref,
    machine_id,
    title,
    description,
    severity,
    status,
    escalated_to
)

work_orders(
    id,
    work_order_ref,
    machine_id,
    title,
    description,
    priority,
    status,
    assigned_to,
    escalated_to
)

maintenance(
    id,
    machine_id,
    activity,
    description,
    technician,
    status,
    maintenance_date
)

IMPORTANT:
maintenance.technician stores technician NAME as text, not technician id.

technicians(
    id,
    name,
    skill,
    status
)

spare_parts(
    id,
    part_code,
    part_name,
    quantity,
    reorder_level
)

production_kpis(
    id,
    machine_id,
    planned_minutes,
    runtime_minutes,
    downtime_minutes,
    total_count,
    good_count,
    reject_count,
    kpi_date,
    ideal_cycle_time
)

Rules:
- Machine status values are usually RUNNING or DOWN.
- Open statuses are usually OPEN.
- Always limit results to 50 rows.
- Use joins when needed.
- Return useful columns only.

Question:
{question}

SQL:
"""

        response = self.llm_service.generate(prompt)
        return self._extract_sql(response)

    def _extract_sql(self, response: str) -> str:
        response = response.strip()
        response = response.replace("```sql", "").replace("```", "").strip()

        match = re.search(r"(SELECT[\s\S]+)", response, re.IGNORECASE)
        if not match:
            raise ValueError("No SELECT SQL found")

        sql = match.group(1).strip().rstrip(";")
        return sql

    def _repair_sql(self, question, failed_sql, error):
        prompt = f"""
A PostgreSQL query failed.

User question:
{question}

Failed SQL:
{failed_sql}

Database error:
{error}

Fix the SQL.

Rules:
- SELECT only
- no explanation
- return only corrected SQL
"""

        response = self.llm_service.generate(prompt)
        return self._extract_sql(response)

    def _validate_sql(self, sql: str) -> str:
        parsed = sqlparse.parse(sql)

        if not parsed:
            raise ValueError("Invalid SQL")

        first = parsed[0].get_type()

        if first != "SELECT":
            raise ValueError("Only SELECT queries are allowed")

        forbidden = [
            "insert",
            "update",
            "delete",
            "drop",
            "alter",
            "truncate",
            "create",
            "grant",
            "revoke"
        ]

        lowered = sql.lower()

        for word in forbidden:
            if re.search(rf"\b{word}\b", lowered):
                raise ValueError(f"Forbidden SQL keyword detected: {word}")

        if "limit" not in lowered:
            sql = sql.rstrip(";") + " LIMIT 50"

        return sql

    def _format_response(self, question, rows):
        safe_rows = [dict(r) for r in rows]

        prompt = f"""
You are GBrain, autonomous manufacturing intelligence assistant.

User Question:
{question}

Retrieved Data:
{json.dumps(safe_rows, default=str)}

Return ONLY valid JSON.

Response format examples:

If machine list:
{{
  "running_machines": [
    {{
      "machine_code": "M-101",
      "name": "CNC Machine",
      "location": "Plant A"
    }}
  ]
}}

If workload:
{{
  "highest_workload_technician": {{
    "name": "Ravi",
    "assigned_count": 3
  }}
}}

Rules:
- ONLY valid JSON
- NO markdown
- NO explanation
- NO SQL mention
- NO internal implementation mention
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
                "answer": safe_rows
            }
