class DynamicQueryRouter:
    def __init__(self, sql_agent, neo4j_agent):
        self.sql_agent = sql_agent
        self.neo4j_agent = neo4j_agent

    def answer(self, question: str):
        q = question.lower()

        graph_keywords = [
            "connected",
            "relationship",
            "dependency",
            "depends",
            "impact",
            "cascade",
            "path",
            "graph",
            "linked",
            "technician workload",
            "handled by",
            "assigned to"
        ]

        if any(word in q for word in graph_keywords):
            return self.neo4j_agent.answer(question)

        return self.sql_agent.answer(question)
