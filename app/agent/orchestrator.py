import json
import logging

from app.agent.planner import AgentPlanner
from app.agent.tool_executor import ToolExecutor
from app.services.ollama_service import OllamaService
from app.services.query_service import DocumentRAGService, QueryService

logger = logging.getLogger("mes_gbrain")


class AgentOrchestrator:
    def __init__(self, db):
        self.db = db
        self.planner = AgentPlanner()
        self.tool_executor = ToolExecutor(db)
        self.llm = OllamaService()
        self.query_service = QueryService(
            self.llm,
            rag_service=DocumentRAGService(db),
        )

    def format(self, question, result):
        if isinstance(result, dict) and result.get("answer"):
            return result["answer"]

        prompt = f"""
You are GBrain.

Summarize the tool result for the user in a concise operational response.
Highlight the most important finding first.

User question:
{question}

Tool result:
{json.dumps(result, default=str, indent=2)}
"""

        try:
            return self.llm.generate(prompt).strip()
        except Exception as exc:
            logger.warning("Agent formatter failed: %s", str(exc))
            return json.dumps(result, default=str)

    def handle(self, question):
        plan = self.planner.plan(question)

        if not plan.get("tool") or not plan.get("action"):
            fallback = self.query_service.ask(question)
            return {
                "plan": plan,
                "result": fallback,
                "answer": self.format(question, fallback),
            }

        result = self.tool_executor.execute(plan)
        final_answer = self.format(question, result)

        return {
            "plan": plan,
            "result": result,
            "answer": final_answer,
        }
