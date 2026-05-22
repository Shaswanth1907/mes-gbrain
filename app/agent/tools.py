TOOLS = [
    {
        "name": "machine_query",
        "description": "Query machine operational data",
    },
    {
        "name": "issue_query",
        "description": "Query issue data",
    },
    {
        "name": "work_order_query",
        "description": "Query work order data",
    },
    {
        "name": "inventory_query",
        "description": "Query spare inventory",
    },
    {
        "name": "maintenance_query",
        "description": "Query maintenance records",
    },
    {
        "name": "graph_query",
        "description": "Neo4j dependency analysis",
    },
    {
        "name": "monitoring_tool",
        "description": "Monitoring and alerts",
    },
    {
        "name": "approval_tool",
        "description": "Approval workflow",
    },
    {
        "name": "execution_tool",
        "description": "Execute maintenance actions",
    },
]

TOOL_ACTIONS = {
    "machine_query": [
        "list_running_machines",
        "list_not_running_machines",
        "list_machines",
        "machine_status",
        "update_machine_status",
    ],
    "issue_query": [
        "create_issue",
        "open_issues",
        "close_issue",
    ],
    "work_order_query": [
        "create_work_order",
        "open_work_orders",
        "close_work_order",
        "assign_work_order",
    ],
    "inventory_query": [
        "check_spare_stock",
        "reserve_spare_stock",
        "low_stock_parts",
    ],
    "maintenance_query": [
        "maintenance_history",
        "create_maintenance",
    ],
    "graph_query": [
        "technician_workload",
        "machines_by_technician",
        "machine_dependency",
        "impact_analysis",
        "graph_explainability",
        "failure_propagation",
    ],
    "monitoring_tool": [
        "run_monitoring_check",
        "show_open_alerts",
    ],
    "approval_tool": [
        "request_approval",
        "approve_execution",
    ],
    "execution_tool": [
        "execute_corrective_plan",
    ],
}
