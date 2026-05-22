import re


class DynamicAgent:
    def plan(self, question: str) -> dict:
        q = question.lower()
        dynamic_plan = None

        if "running" in q and "machine" in q:
            dynamic_plan = {
                "tool": "machine_query",
                "action": "list_running_machines",
                "params": {}
            }
        elif "all machines" in q or "list machines" in q:
            dynamic_plan = {
                "tool": "machine_query",
                "action": "list_all_machines",
                "params": {}
            }
        elif "open issues" in q or "open issue" in q:
            dynamic_plan = {
                "tool": "issue_query",
                "action": "list_open_issues",
                "params": {}
            }
        elif "open work orders" in q or "active work orders" in q:
            dynamic_plan = {
                "tool": "work_order_query",
                "action": "list_open_work_orders",
                "params": {}
            }
        elif "low stock" in q or "reorder" in q:
            dynamic_plan = {
                "tool": "inventory_query",
                "action": "list_low_stock_parts",
                "params": {}
            }
        elif "technician workload" in q:
            dynamic_plan = {
                "tool": "graph_query",
                "action": "technician_workload",
                "params": {}
            }
        else:
            machine_code = self.extract_machine_code(question)

            if "dependency" in q and machine_code:
                dynamic_plan = {
                    "tool": "graph_query",
                    "action": "machine_dependency",
                    "params": {
                        "machine_code": machine_code
                    }
                }
            else:
                dynamic_plan = {
                    "tool": "general",
                    "action": "fallback",
                    "params": {
                        "question": question
                    }
                }

        print("DYNAMIC PLAN:", dynamic_plan)

        return dynamic_plan

    def extract_machine_code(self, question: str) -> str:
        match = re.search(r"(M-\d+)", question.upper())
        return match.group(1) if match else ""
