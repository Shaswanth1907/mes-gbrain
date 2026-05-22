import json
import logging
import re

from app.agent.planner_prompt import PLANNER_PROMPT
from app.agent.tools import TOOLS, TOOL_ACTIONS
from app.services.ollama_service import OllamaService
from app.services.planner_service import PlannerService

logger = logging.getLogger("mes_gbrain")


class AgentPlanner:
    def __init__(self):
        self.ollama = OllamaService()
        self.legacy_planner = PlannerService()

    def _clean_json(self, raw_response):
        return re.sub(r"```json|```", "", raw_response).strip()

    def _normalize(self, plan):
        normalized = {
            "tool": str(plan.get("tool", "")).strip(),
            "action": str(plan.get("action", "")).strip(),
            "params": plan.get("params") or {},
        }

        if not isinstance(normalized["params"], dict):
            raise ValueError("Planner params must be a JSON object")

        tool = normalized["tool"]
        action = normalized["action"]

        if tool not in TOOL_ACTIONS:
            raise ValueError(f"Unsupported tool: {tool}")

        if action not in TOOL_ACTIONS[tool]:
            raise ValueError(f"Unsupported action '{action}' for tool '{tool}'")

        return normalized

    def _translate_legacy_plan(self, legacy_plan):
        intent = legacy_plan.get("intent")

        intent_map = {
            "list_running_machines": {
                "tool": "machine_query",
                "action": "list_running_machines",
                "params": {},
            },
            "list_not_running_machines": {
                "tool": "machine_query",
                "action": "list_not_running_machines",
                "params": {},
            },
            "list_machines": {
                "tool": "machine_query",
                "action": "list_machines",
                "params": {
                    "status": legacy_plan.get("status", ""),
                },
            },
            "machine_status": {
                "tool": "machine_query",
                "action": "machine_status",
                "params": {
                    "machine_code": legacy_plan.get("machine_code", ""),
                },
            },
            "update_machine_status": {
                "tool": "machine_query",
                "action": "update_machine_status",
                "params": {
                    "machine_code": legacy_plan.get("machine_code", ""),
                    "status": legacy_plan.get("status", ""),
                },
            },
            "create_issue": {
                "tool": "issue_query",
                "action": "create_issue",
                "params": {
                    "machine_code": legacy_plan.get("machine_code", ""),
                    "severity": legacy_plan.get("severity", "MEDIUM"),
                },
            },
            "open_issues": {
                "tool": "issue_query",
                "action": "open_issues",
                "params": {
                    "machine_code": legacy_plan.get("machine_code", ""),
                },
            },
            "close_issue": {
                "tool": "issue_query",
                "action": "close_issue",
                "params": {
                    "issue_ref": legacy_plan.get("issue_ref", ""),
                },
            },
            "create_work_order": {
                "tool": "work_order_query",
                "action": "create_work_order",
                "params": {
                    "machine_code": legacy_plan.get("machine_code", ""),
                    "priority": legacy_plan.get("priority", "MEDIUM"),
                },
            },
            "open_work_orders": {
                "tool": "work_order_query",
                "action": "open_work_orders",
                "params": {
                    "machine_code": legacy_plan.get("machine_code", ""),
                },
            },
            "close_work_order": {
                "tool": "work_order_query",
                "action": "close_work_order",
                "params": {
                    "work_order_ref": legacy_plan.get("work_order_ref", ""),
                },
            },
            "assign_work_order": {
                "tool": "work_order_query",
                "action": "assign_work_order",
                "params": {
                    "work_order_ref": legacy_plan.get("work_order_ref", ""),
                    "technician": legacy_plan.get("assigned_to", ""),
                },
            },
            "check_spare_stock": {
                "tool": "inventory_query",
                "action": "check_spare_stock",
                "params": {
                    "part_code": legacy_plan.get("part_code", ""),
                },
            },
            "reserve_spare_stock": {
                "tool": "inventory_query",
                "action": "reserve_spare_stock",
                "params": {
                    "part_code": legacy_plan.get("part_code", ""),
                    "quantity": legacy_plan.get("quantity", 0),
                },
            },
            "low_stock_parts": {
                "tool": "inventory_query",
                "action": "low_stock_parts",
                "params": {},
            },
            "maintenance_history": {
                "tool": "maintenance_query",
                "action": "maintenance_history",
                "params": {
                    "machine_code": legacy_plan.get("machine_code", ""),
                },
            },
            "create_maintenance": {
                "tool": "maintenance_query",
                "action": "create_maintenance",
                "params": {
                    "machine_code": legacy_plan.get("machine_code", ""),
                    "activity": legacy_plan.get("activity", ""),
                    "assigned_to": legacy_plan.get("assigned_to", ""),
                },
            },
            "graph_technician_workload": {
                "tool": "graph_query",
                "action": "technician_workload",
                "params": {},
            },
            "graph_machines_by_technician": {
                "tool": "graph_query",
                "action": "machines_by_technician",
                "params": {
                    "technician": legacy_plan.get("technician", ""),
                },
            },
            "graph_machine_dependency": {
                "tool": "graph_query",
                "action": "machine_dependency",
                "params": {
                    "machine_code": legacy_plan.get("machine_code", ""),
                },
            },
            "graph_impact_analysis": {
                "tool": "graph_query",
                "action": "impact_analysis",
                "params": {
                    "machine_code": legacy_plan.get("machine_code", ""),
                },
            },
            "graph_explainability": {
                "tool": "graph_query",
                "action": "graph_explainability",
                "params": {
                    "machine_code": legacy_plan.get("machine_code", ""),
                },
            },
            "failure_propagation": {
                "tool": "graph_query",
                "action": "failure_propagation",
                "params": {
                    "machine_code": legacy_plan.get("machine_code", ""),
                },
            },
            "run_monitoring_check": {
                "tool": "monitoring_tool",
                "action": "run_monitoring_check",
                "params": {},
            },
            "show_open_alerts": {
                "tool": "monitoring_tool",
                "action": "show_open_alerts",
                "params": {},
            },
            "request_approval": {
                "tool": "approval_tool",
                "action": "request_approval",
                "params": {
                    "machine_code": legacy_plan.get("machine_code", ""),
                },
            },
            "approve_execution": {
                "tool": "approval_tool",
                "action": "approve_execution",
                "params": {
                    "approval_ref": legacy_plan.get("approval_ref", ""),
                },
            },
            "execute_corrective_plan": {
                "tool": "execution_tool",
                "action": "execute_corrective_plan",
                "params": {
                    "machine_code": legacy_plan.get("machine_code", ""),
                },
            },
        }

        translated = intent_map.get(intent)

        if not translated:
            return None

        return self._normalize(translated)

    def plan(self, question):
        legacy_plan = self.legacy_planner.fallback_plan(question)
        translated = self._translate_legacy_plan(legacy_plan)

        if translated:
            logger.info("Agent planner used deterministic fallback | plan=%s", translated)
            return translated

        prompt = PLANNER_PROMPT.format(
            tools=json.dumps(TOOLS, indent=2),
            tool_actions=json.dumps(TOOL_ACTIONS, indent=2),
            question=question,
        )

        try:
            raw_response = self.ollama.generate(prompt)
            parsed = json.loads(self._clean_json(raw_response))
            normalized = self._normalize(parsed)
            logger.info("Agent planner used LLM plan | plan=%s", normalized)
            return normalized
        except Exception as exc:
            logger.error("Agent planner failed: %s", str(exc))
            return {
                "tool": "",
                "action": "",
                "params": {},
            }
