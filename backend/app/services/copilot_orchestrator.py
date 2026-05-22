from app.dynamic_query.dynamic_query_router import DynamicQueryRouter
from app.dynamic_query.neo4j_agent import Neo4jAgent
from app.dynamic_query.sql_agent import SQLAgent
from app.services.planner_service import PlannerService
from app.services.query_service import QueryService, DocumentRAGService
from app.services.issue_service import IssueService
from app.services.machine_service import MachineService
from app.services.maintenance_service import MaintenanceService
from app.services.predictive_service import PredictiveService
from app.services.anomaly_detection_service import AnomalyDetectionService
from app.services.production_kpi_service import ProductionKPIService
from app.services.production_optimization_service import ProductionOptimizationService
from app.services.monitoring_service import MonitoringService
from app.services.root_cause_service import RootCauseService
from app.services.shift_summary_service import ShiftSummaryService
from app.services.factory_summary_service import FactorySummaryService
from app.services.failure_advisor_service import FailureAdvisorService
from app.services.auto_work_order_service import AutoWorkOrderService
from app.services.escalation_service import EscalationService
from app.services.spare_part_service import SparePartService
from app.services.technician_service import TechnicianService
from app.services.work_order_service import WorkOrderService
from app.services.spare_impact_service import SpareImpactService
from app.services.autonomous_maintenance_planner import AutonomousMaintenancePlanner
from app.services.execute_corrective_plan_service import ExecuteCorrectivePlanService
from app.services.approval_service import ApprovalService
from app.services.feedback_learning_service import FeedbackLearningService
from app.services.ollama_service import OllamaService
from app.graph.graph_query_service import GraphQueryService
import logging

logger = logging.getLogger("mes_gbrain")


class CopilotOrchestrator:
    def __init__(self, db):
        self.db = db
        self.planner = PlannerService()
        self.llm_service = OllamaService()
        self.query_service = QueryService(
            self.llm_service,
            rag_service=DocumentRAGService(db)
        )
        self.issue_service = IssueService(db)
        self.machine_service = MachineService(db)
        self.maintenance_service = MaintenanceService(db)
        self.predictive_service = PredictiveService(db)
        self.anomaly_service = AnomalyDetectionService(db)
        self.production_kpi_service = ProductionKPIService(db)
        self.production_optimization_service = ProductionOptimizationService(db)
        self.monitoring_service = MonitoringService(db)
        self.root_cause_service = RootCauseService(db)
        self.shift_summary_service = ShiftSummaryService(db)
        self.factory_summary_service = FactorySummaryService(db)
        self.failure_advisor_service = FailureAdvisorService(db)
        self.auto_work_order_service = AutoWorkOrderService(db)
        self.escalation_service = EscalationService(db)
        self.spare_part_service = SparePartService(db)
        self.spare_impact_service = SpareImpactService(db)
        self.maintenance_planner = AutonomousMaintenancePlanner(db)
        self.execute_plan_service = ExecuteCorrectivePlanService(db)
        self.approval_service = ApprovalService(db)
        self.feedback_learning_service = FeedbackLearningService(db)
        self.technician_service = TechnicianService(db)
        self.work_order_service = WorkOrderService(db)
        self.graph_query_service = GraphQueryService()
        self.sql_agent = SQLAgent(db, self.llm_service)
        self.neo4j_agent = Neo4jAgent(self.llm_service)
        self.dynamic_query_router = DynamicQueryRouter(
            self.sql_agent,
            self.neo4j_agent
        )

    def handle(self, question):
        try:
            logger.info(f"Copilot request received | question={question}")

            plan = self.planner.plan(question)
            print("PLANNER PLAN:", plan)

            logger.info(f"Planner completed | plan={plan}")

            intent = plan.get("intent")
            print("INTENT:", intent)

            if intent == "create_issue":
                return self.issue_service.create_issue(
                    machine_code=plan.get("machine_code"),
                    description=question,
                    severity=plan.get("severity", "MEDIUM")
                )

            elif intent == "list_not_running_machines":
                return self.machine_service.get_not_running_machines()

            elif intent in [
                "unknown",
                "general_question"
            ]:
                return self.dynamic_query_router.answer(question)

            elif intent == "machine_status":
                return self.machine_service.get_machine_status(
                    plan.get("machine_code")
                )

            elif intent == "update_machine_status":
                return self.machine_service.update_machine_status(
                    plan["machine_code"],
                    plan["status"]
                )

            elif intent == "close_issue":
                return self.issue_service.close_issue(
                    plan.get("issue_ref")
                )

            elif intent == "maintenance_history":
                return self.maintenance_service.get_history(
                    plan.get("machine_code")
                )

            elif intent == "predictive_maintenance":
                return self.predictive_service.predict_failure_risk(
                    plan["machine_code"]
                )

            elif intent == "anomaly_detection":
                return self.anomaly_service.detect(
                    plan["machine_code"]
                )

            elif intent == "production_kpi":
                return self.production_kpi_service.get_machine_kpi(
                    plan["machine_code"]
                )

            elif intent == "production_optimization":
                return self.production_optimization_service.optimize_machine(
                    plan["machine_code"]
                )

            elif intent == "shift_summary":
                return self.shift_summary_service.summarize_machine_shift(
                    plan["machine_code"]
                )

            elif intent == "factory_summary":
                return self.factory_summary_service.summarize_factory()

            elif intent == "run_monitoring_check":
                return self.monitoring_service.run_check()

            elif intent == "show_open_alerts":
                return self.monitoring_service.get_open_alerts()

            elif intent == "failure_advisor":
                return self.failure_advisor_service.advise(
                    plan["machine_code"]
                )

            elif intent == "recommend_work_order":
                return self.auto_work_order_service.recommend(
                    plan["machine_code"]
                )

            elif intent == "create_recommended_work_order":
                return self.auto_work_order_service.create_recommended(
                    plan["machine_code"]
                )

            elif intent == "root_cause_analysis":
                return self.root_cause_service.analyze(
                    plan["machine_code"]
                )

            elif intent == "create_maintenance":
                return self.maintenance_service.create_maintenance(
                    plan["machine_code"],
                    plan["activity"],
                    question,
                    plan["assigned_to"]
                )

            elif intent == "check_spare_stock":
                return self.spare_part_service.check_stock(
                    plan["part_code"]
                )

            elif intent == "reserve_spare_stock":
                return self.spare_part_service.reserve_stock(
                    plan["part_code"],
                    plan["quantity"]
                )

            elif intent == "spare_impact_analysis":
                return self.spare_impact_service.assess(
                    plan["machine_code"]
                )

            elif intent == "autonomous_maintenance_plan":
                return self.maintenance_planner.plan(
                    plan["machine_code"]
                )

            elif intent == "execute_corrective_plan":
                return self.execute_plan_service.execute(
                    plan["machine_code"]
                )

            elif intent == "request_approval":
                return self.approval_service.request_approval(
                    plan["machine_code"]
                )

            elif intent == "approve_execution":
                return self.approval_service.approve(
                    plan["approval_ref"]
                )

            elif intent == "record_feedback":
                return self.feedback_learning_service.record_outcome(
                    machine_code=plan["machine_code"],
                    action_type="Corrective Maintenance",
                    predicted_downtime=45,
                    actual_downtime=72,
                    predicted_technician="Kumar",
                    actual_technician="Kumar",
                    predicted_part="BR-220",
                    actual_part="BR-220",
                    success=True,
                    notes="Recorded from AI feedback test"
                )

            elif intent == "feedback_insights":
                return self.feedback_learning_service.insights(
                    machine_code=plan["machine_code"] or None
                )

            elif intent == "graph_technician_workload":
                return self.graph_query_service.technician_workload()

            elif intent == "graph_machines_by_technician":
                return self.graph_query_service.machines_handled_by_technician(
                    plan["technician"]
                )

            elif intent == "graph_machine_dependency":
                return self.graph_query_service.machine_dependency_view(
                    plan["machine_code"]
                )

            elif intent == "graph_impact_analysis":
                return self.graph_query_service.impact_analysis(
                    plan["machine_code"]
                )

            elif intent == "graph_explainability":
                return self.graph_query_service.graph_explainability(
                    plan["machine_code"]
                )

            elif intent == "failure_propagation":
                try:
                    print("FAILURE PROPAGATION PLAN:", plan)

                    return self.graph_query_service.failure_propagation(
                        plan["machine_code"]
                    )

                except Exception as e:
                    import traceback
                    print(traceback.format_exc())
                    raise

            elif intent == "create_work_order":
                return self.work_order_service.create_work_order(
                    machine_code=plan["machine_code"],
                    description=question,
                    priority=plan["priority"]
                )

            elif intent == "close_work_order":
                return self.work_order_service.close_work_order(
                    plan.get("work_order_ref")
                )

            elif intent == "assign_work_order":
                return self.work_order_service.assign_work_order(
                    plan["work_order_ref"],
                    plan["assigned_to"]
                )

            elif intent == "escalate_issue":
                return self.escalation_service.escalate_issue(
                    plan["issue_ref"],
                    plan["assigned_to"]
                )

            elif intent == "escalate_work_order":
                return self.escalation_service.escalate_work_order(
                    plan["work_order_ref"],
                    plan["assigned_to"]
                )

            else:
                return self.dynamic_query_router.answer(question)

        except Exception as e:
            logger.error(f"Copilot orchestrator failed: {str(e)}")
            return {
                "message": "Copilot request failed"
            }
