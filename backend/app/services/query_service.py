from app.repositories.document_repository import DocumentRepository


class DocumentRAGService:
    def __init__(self, db):
        self.repo = DocumentRepository(db)

    def retrieve(self, question):
        docs = self.repo.search_documents(question)
        return [doc.content for doc in docs if doc.content]


class QueryService:
    def __init__(self, llm_service, rag_service=None):
        self.llm_service = llm_service
        self.rag_service = rag_service

    def answer_general_question(self, question):
        prompt = f"""
You are GBrain.

You are an autonomous manufacturing operations intelligence system.

Answer this:
{question}
"""

        response = self.llm_service.generate(prompt)

        return {
            "answer": response
        }

    def ask(self, question):
        return self.answer_general_question(question)
