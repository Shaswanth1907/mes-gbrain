import json
import re
import logging

from app.services.ollama_service import OllamaService

logger = logging.getLogger("mes_gbrain")


class PlannerService:
    def __init__(self):
        self.ollama = OllamaService()

    def extract_machine_code(self, question):
        match = re.search(r"(M-\d+)", question.upper())
        return match.group(1) if match else None

    def extract_issue_ref(self, question):
        match = re.search(r"\b[a-f0-9]{8}\b", question.lower())
        return match.group(0) if match else ""

    def extract_work_order_ref(self, question):
        match = re.search(r"(WO-[A-Za-z0-9\-]+)", question)
        return match.group(1) if match else ""

    def extract_approval_ref(self, question):
        match = re.search(r"APR-[A-Za-z0-9]+", question)
        return match.group(0) if match else ""

    def extract_part_code(self, question):
        match = re.search(r"\b([A-Z]{2,}-\d+)\b", question.upper())
        return match.group(1) if match else None

    def extract_assigned_to(self, question):
        patterns = [
            r"assign\s+work\s+order\s+WO-[A-Z0-9]+\s+to\s+technician\s+([A-Z][A-Z\s\-']+)",
            r"assign\s+work\s+order\s+WO-[A-Z0-9]+\s+to\s+([A-Z][A-Z\s\-']+)",
            r"assign\s+WO-[A-Z0-9]+\s+to\s+technician\s+([A-Z][A-Z\s\-']+)",
            r"assign\s+WO-[A-Z0-9]+\s+to\s+([A-Z][A-Z\s\-']+)",
            r"with\s+technician\s+([A-Z][A-Z\s\-']+)",
            r"technician\s+([A-Z][A-Z\s\-']+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                assigned_to = match.group(1).strip()
                return assigned_to.title()

        return None

    def extract_severity(self, question):
        q = question.lower()

        if "critical" in q:
            return "CRITICAL"
        elif "high" in q:
            return "HIGH"
        elif "medium" in q:
            return "MEDIUM"
        elif "low" in q:
            return "LOW"

        return "MEDIUM"

    def extract_priority(self, question):
        q = question.lower()

        if "urgent" in q:
            return "URGENT"
        elif "high" in q:
            return "HIGH"
        elif "medium" in q:
            return "MEDIUM"
        elif "low" in q:
            return "LOW"

        return "MEDIUM"

    def extract_status(self, question):
        q = question.lower()

        if " stopped" in f" {q}" or " as stopped" in q:
            return "DOWN"
        elif " down" in f" {q}" or " as down" in q:
            return "DOWN"
        elif " running" in f" {q}" or " as running" in q:
            return "RUNNING"
        elif " idle" in f" {q}" or " as idle" in q:
            return "IDLE"
        elif " maintenance" in f" {q}" or " as maintenance" in q:
            return "MAINTENANCE"
        elif " offline" in f" {q}" or " as offline" in q:
            return "OFFLINE"

        return ""

    def extract_activity(self, question):
        q = question.lower()

        if "preventive maintenance" in q:
            return "Preventive Maintenance"
        elif "corrective maintenance" in q:
            return "Corrective Maintenance"
        elif "maintenance" in q:
            return "Maintenance"

        return ""

    def extract_quantity(self, question):
        match = re.search(r"\b(\d+)\b", question)
        return int(match.group(1)) if match else 0

    def extract_technician(self, question):
        patterns = [
            r"assigned\s+to\s+([A-Z][A-Z\s\-']+)",
            r"work\s+assigned\s+to\s+([A-Z][A-Z\s\-']+)",
            r"tasks\s+does\s+technician\s+([A-Z][A-Z\s\-']+?)\s+have",
            r"technician\s+([A-Z][A-Z\-']+(?:\s+[A-Z][A-Z\-']+)*)\b(?:\s+have|\?|$)"
        ]

        for pattern in patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                return match.group(1).strip().title()

        return None

    def extract_name(self, question):
        patterns = [
            r"machines\s+handled\s+by\s+([A-Z][A-Z\s\-']+)",
            r"handled\s+by\s+([A-Z][A-Z\s\-']+)",
            r"technician\s+([A-Z][A-Z\s\-']+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                return match.group(1).strip().title()

        return ""

    def extract_escalation_target(self, question):
        q = question.lower()

        if "maintenance manager" in q:
            return "maintenance manager"

        if "plant supervisor" in q:
            return "plant supervisor"

        if "supervisor" in q:
            return "supervisor"

        return "manager"

    def build_plan(
        self,
        intent="general_question",
        machine_code="",
        issue_ref="",
        work_order_ref="",
        approval_ref="",
        assigned_to="",
        severity="",
        priority="",
        status="",
        activity="",
        part_code="",
        quantity=0,
        technician=""
    ):
        return {
            "intent": intent or "",
            "machine_code": machine_code or "",
            "issue_ref": issue_ref or "",
            "work_order_ref": work_order_ref or "",
            "approval_ref": approval_ref or "",
            "assigned_to": assigned_to or "",
            "severity": severity or "",
            "priority": priority or "",
            "status": status or "",
            "activity": activity or "",
            "part_code": part_code or "",
            "quantity": quantity or 0,
            "technician": technician or ""
        }

    def normalize_intent(self, intent):
        intent_map = {
            "get_open_issues": "open_issues",
            "general_query": "general_question",
            "production_summary": "production_kpi"
        }
        return intent_map.get(intent, intent)

    def fallback_plan(self, question):
        q = question.lower()

        if "open issues" in q or "open issue" in q:
            return self.build_plan(intent="general_question")

        if "open work orders" in q or "active work orders" in q:
            return self.build_plan(intent="general_question")

        if "create issue" in q or "report issue" in q:
            return self.build_plan(
                intent="create_issue",
                machine_code=self.extract_machine_code(question),
                severity=self.extract_severity(question)
            )

        elif "not running" in q and "machine" in q:
            return self.build_plan(
                intent="list_not_running_machines"
            )

        elif "running" in q and "machine" in q:
            return self.build_plan(
                intent="list_running_machines"
            )

        elif (
            "all machines" in q
            or "every machine" in q
            or "every machines" in q
            or ("show" in q and "machines" in q and any(
                word in q for word in ["running", "down", "idle", "offline", "maintenance"]
            ))
        ):
            return self.build_plan(
                intent="list_machines",
                status=self.extract_status(question)
            )

        elif "status" in q and "machine" in q:
            return self.build_plan(
                intent="machine_status",
                machine_code=self.extract_machine_code(question)
            )

        elif "mark machine" in q and " as " in q:
            return self.build_plan(
                intent="update_machine_status",
                machine_code=self.extract_machine_code(question),
                status=self.extract_status(question)
            )

        elif "root cause" in q or "repeatedly overheating" in q:
            return self.build_plan(
                intent="root_cause_analysis",
                machine_code=self.extract_machine_code(question)
            )

        elif "risk of failure" in q or "predict failure risk" in q:
            return self.build_plan(
                intent="predictive_maintenance",
                machine_code=self.extract_machine_code(question)
            )

        elif "detect abnormal" in q or "anomaly" in q:
            return self.build_plan(
                intent="anomaly_detection",
                machine_code=self.extract_machine_code(question)
            )

        elif "shift summary" in q or "summarize today's production" in q or "summarize production" in q:
            return self.build_plan(
                intent="shift_summary",
                machine_code=self.extract_machine_code(question)
            )

        elif "factory performance" in q or "factory summary" in q:
            return self.build_plan(
                intent="factory_summary"
            )

        elif (
            "run monitoring" in q
            or "monitoring check" in q
            or "check factory alerts" in q
        ):
            return self.build_plan(
                intent="run_monitoring_check"
            )

        elif "show open alerts" in q or "show alerts" in q:
            return self.build_plan(
                intent="show_open_alerts"
            )

        elif "record feedback" in q or "record outcome" in q:
            return self.build_plan(
                intent="record_feedback",
                machine_code=self.extract_machine_code(question)
            )

        elif "learning insights" in q or "feedback insights" in q:
            return self.build_plan(
                intent="feedback_insights",
                machine_code=self.extract_machine_code(question)
            )

        elif "request corrective execution approval" in q:
            return self.build_plan(
                intent="request_approval",
                machine_code=self.extract_machine_code(question)
            )

        elif "approve execution" in q:
            return self.build_plan(
                intent="approve_execution",
                approval_ref=self.extract_approval_ref(question)
            )

        elif (
            "execute corrective plan" in q
            or "execute plan" in q
        ):
            return self.build_plan(
                intent="execute_corrective_plan",
                machine_code=self.extract_machine_code(question)
            )

        elif (
            "plan corrective action" in q
            or "maintenance plan" in q
            or ("high risk" in q and "plan" in q)
        ):
            return self.build_plan(
                intent="autonomous_maintenance_plan",
                machine_code=self.extract_machine_code(question)
            )

        elif "recommended work order" in q:
            return self.build_plan(
                intent="create_recommended_work_order",
                machine_code=self.extract_machine_code(question)
            )

        elif "should i create a work order" in q:
            return self.build_plan(
                intent="recommend_work_order",
                machine_code=self.extract_machine_code(question)
            )

        elif "technician workload" in q:
            return self.build_plan(
                intent="graph_technician_workload"
            )

        elif "machines handled by" in q:
            return self.build_plan(
                intent="graph_machines_by_technician",
                technician=self.extract_name(question)
            )

        elif "dependency view" in q or "connected entities" in q:
            return self.build_plan(
                intent="graph_machine_dependency",
                machine_code=self.extract_machine_code(question)
            )

        elif "why is machine" in q and "high risk" in q:
            return self.build_plan(
                intent="graph_explainability",
                machine_code=self.extract_machine_code(question)
            )

        elif "impacted if machine" in q or "impact analysis" in q:
            return self.build_plan(
                intent="graph_impact_analysis",
                machine_code=self.extract_machine_code(question)
            )

        elif (
            "required spare parts" in q
            or ("spare parts" in q and "fails" in q)
            or "inventory impact" in q
        ):
            return self.build_plan(
                intent="spare_impact_analysis",
                machine_code=self.extract_machine_code(question)
            )

        elif (
            "failure propagation" in q
            or "cascade effects" in q
            or ("machine" in q and "fails" in q)
        ):
            return self.build_plan(
                intent="failure_propagation",
                machine_code=self.extract_machine_code(question)
            )

        elif (
            "improve production" in q
            or "optimize production" in q
            or "improve throughput" in q
            or "production throughput" in q
        ):
            return self.build_plan(
                intent="production_optimization",
                machine_code=self.extract_machine_code(question)
            )

        elif "reduce failures" in q or "prevent failure" in q or "avoid failure" in q:
            return self.build_plan(
                intent="failure_advisor",
                machine_code=self.extract_machine_code(question)
            )

        elif (
            "oee" in q or
            "uptime" in q or
            "downtime" in q or
            "kpi" in q or
            ("production" in q and ("summary" in q or "summarize" in q))
        ):
            machine_code = ""

            match = re.search(r"(M-\d+)", question)

            if match:
                machine_code = match.group(1)

            return self.build_plan(
                intent="production_kpi",
                machine_code=machine_code
            )

        elif "schedule" in q and "maintenance" in q:
            return self.build_plan(
                intent="create_maintenance",
                machine_code=self.extract_machine_code(question),
                assigned_to=self.extract_assigned_to(question),
                activity=self.extract_activity(question)
            )

        elif "check stock" in q or ("stock" in q and self.extract_part_code(question)):
            return self.build_plan(
                intent="check_spare_stock",
                part_code=self.extract_part_code(question)
            )

        elif "reserve" in q and self.extract_part_code(question):
            return self.build_plan(
                intent="reserve_spare_stock",
                part_code=self.extract_part_code(question),
                quantity=self.extract_quantity(question)
            )

        elif "low stock" in q and "part" in q:
            return self.build_plan(
                intent="low_stock_parts"
            )

        elif "assigned to" in q or ("technician" in q and "task" in q) or ("technician" in q and "work" in q):
            return self.build_plan(
                intent="technician_workload",
                technician=self.extract_technician(question)
            )

        elif "open issues" in q:
            return self.build_plan(
                intent="open_issues",
                machine_code=self.extract_machine_code(question)
            )

        elif "close issue" in q:
            return self.build_plan(
                intent="close_issue",
                issue_ref=self.extract_issue_ref(question)
            )

        elif "escalate issue" in q:
            return self.build_plan(
                intent="escalate_issue",
                issue_ref=self.extract_issue_ref(question),
                assigned_to=self.extract_escalation_target(question)
            )

        elif "maintenance" in q:
            return self.build_plan(
                intent="maintenance_history",
                machine_code=self.extract_machine_code(question)
            )

        elif (
            "create work order" in q or
            "urgent work order" in q or
            "generate work order" in q
        ):
            return self.build_plan(
                intent="create_work_order",
                machine_code=self.extract_machine_code(question),
                priority="URGENT" if "urgent" in q else self.extract_priority(question)
            )

        elif "open work orders" in q or "work orders" in q:
            return self.build_plan(
                intent="open_work_orders",
                machine_code=self.extract_machine_code(question)
            )

        elif "close work order" in q:
            return self.build_plan(
                intent="close_work_order",
                work_order_ref=self.extract_work_order_ref(question)
            )

        elif "escalate work order" in q:
            return self.build_plan(
                intent="escalate_work_order",
                work_order_ref=self.extract_work_order_ref(question),
                assigned_to=self.extract_escalation_target(question)
            )

        elif "assign work order" in q or ("assign" in q and "wo-" in q):
            return self.build_plan(
                intent="assign_work_order",
                work_order_ref=self.extract_work_order_ref(question),
                assigned_to=self.extract_assigned_to(question)
            )

        return self.build_plan(intent="general_question")

    def plan(self, question: str):
        try:
            fallback = self.fallback_plan(question)

            # Fast-path deterministic intents so the app does not block on
            # Ollama for straightforward operational requests.
            if fallback.get("intent") != "general_question":
                logger.info(f"Planner shortcut used | plan={fallback}")
                return fallback

            prompt = f"""
Extract MES intent from user query.

Return ONLY valid JSON.

Schema:
{{
  "intent": "",
  "machine_code": "",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Examples:

Show open issues for machine M-101
{{
  "intent": "open_issues",
  "machine_code": "M-101",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Close issue f5f9e6ec
{{
  "intent": "close_issue",
  "machine_code": "",
  "issue_ref": "f5f9e6ec",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Create urgent work order for machine M-101 bearing overheating
{{
  "intent": "create_work_order",
  "machine_code": "M-101",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "HIGH",
  "priority": "URGENT",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Assign work order WO-6c8a0a96 to technician John
{{
  "intent": "assign_work_order",
  "machine_code": "",
  "issue_ref": "",
  "work_order_ref": "WO-6c8a0a96",
  "approval_ref": "",
  "assigned_to": "John",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Escalate issue 0507faf0 to maintenance manager
{{
  "intent": "escalate_issue",
  "machine_code": "",
  "issue_ref": "0507faf0",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "maintenance manager",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Escalate work order WO-6c8a0a96 to plant supervisor
{{
  "intent": "escalate_work_order",
  "machine_code": "",
  "issue_ref": "",
  "work_order_ref": "WO-6c8a0a96",
  "approval_ref": "",
  "assigned_to": "plant supervisor",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Mark machine M-101 as DOWN
{{
  "intent": "update_machine_status",
  "machine_code": "M-101",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "DOWN",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Schedule preventive maintenance for machine M-101 with technician Ravi
{{
  "intent": "create_maintenance",
  "machine_code": "M-101",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "Ravi",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "Preventive Maintenance",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Check stock for bearing BR-220
{{
  "intent": "check_spare_stock",
  "machine_code": "",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "BR-220",
  "quantity": 0,
  "technician": ""
}}

Reserve 2 bearings BR-220
{{
  "intent": "reserve_spare_stock",
  "machine_code": "",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "BR-220",
  "quantity": 2,
  "technician": ""
}}

Show low stock spare parts
{{
  "intent": "low_stock_parts",
  "machine_code": "",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Show work assigned to Ravi
{{
  "intent": "technician_workload",
  "machine_code": "",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": "Ravi"
}}

What tasks does technician John have?
{{
  "intent": "technician_workload",
  "machine_code": "",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": "John"
}}

Is machine M-101 at risk of failure?
{{
  "intent": "predictive_maintenance",
  "machine_code": "M-101",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Predict failure risk for machine M-101
{{
  "intent": "predictive_maintenance",
  "machine_code": "M-101",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Detect abnormal behavior for machine M-103
{{
  "intent": "anomaly_detection",
  "machine_code": "M-103",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Show production KPI for machine M-101
{{
  "intent": "production_kpi",
  "machine_code": "M-101",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Calculate OEE for machine M-101
{{
  "intent": "production_kpi",
  "machine_code": "M-101",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Show uptime for machine M-101
{{
  "intent": "production_kpi",
  "machine_code": "M-101",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Show downtime for machine M-101
{{
  "intent": "production_kpi",
  "machine_code": "M-101",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

How can we reduce failures on machine M-101?
{{
  "intent": "failure_advisor",
  "machine_code": "M-101",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Summarize today's production for machine M-101
{{
  "intent": "shift_summary",
  "machine_code": "M-101",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Summarize today's factory performance
{{
  "intent": "factory_summary",
  "machine_code": "",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Should I create a work order for machine M-101?
{{
  "intent": "recommend_work_order",
  "machine_code": "M-101",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Create recommended work order for machine M-101
{{
  "intent": "create_recommended_work_order",
  "machine_code": "M-101",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Why is machine M-101 repeatedly overheating?
{{
  "intent": "root_cause_analysis",
  "machine_code": "M-101",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

Find root cause for machine M-101 overheating
{{
  "intent": "root_cause_analysis",
  "machine_code": "M-101",
  "issue_ref": "",
  "work_order_ref": "",
  "approval_ref": "",
  "assigned_to": "",
  "severity": "",
  "priority": "",
  "status": "",
  "activity": "",
  "part_code": "",
  "quantity": 0,
  "technician": ""
}}

User query:
{question}
"""

            raw = self.ollama.generate(prompt)

            cleaned = re.sub(r"```json|```", "", raw).strip()

            logger.info(f"Planner cleaned response: {cleaned}")

            parsed = json.loads(cleaned)

            # normalize casing
            if parsed.get("severity"):
                parsed["severity"] = str(parsed["severity"]).upper()

            if parsed.get("priority"):
                parsed["priority"] = str(parsed["priority"]).upper()

            if parsed.get("status"):
                parsed["status"] = str(parsed["status"]).upper()

            normalized_intent = self.normalize_intent(parsed.get("intent", ""))
            machine_code = parsed.get("machine_code", "")

            if normalized_intent == "failure_propagation" and not machine_code:
                machine_code = self.extract_machine_code(question) or ""

            return self.build_plan(
                intent=normalized_intent,
                machine_code=machine_code,
                issue_ref=parsed.get("issue_ref", ""),
                work_order_ref=parsed.get("work_order_ref", ""),
                approval_ref=parsed.get("approval_ref", ""),
                assigned_to=parsed.get("assigned_to", ""),
                severity=parsed.get("severity", ""),
                priority=parsed.get("priority", ""),
                status=parsed.get("status", ""),
                activity=parsed.get("activity", ""),
                part_code=parsed.get("part_code", ""),
                quantity=int(parsed.get("quantity", 0) or 0),
                technician=parsed.get("technician", "")
            )

        except Exception as e:
            logger.error(f"Planner failed: {str(e)}")

            fallback = self.fallback_plan(question)

            logger.info(f"Planner fallback used | plan={fallback}")

            return fallback
