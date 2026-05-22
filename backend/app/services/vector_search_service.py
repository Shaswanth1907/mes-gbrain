from app.core.logger import logger
from app.models.document import DocumentChunk
from app.services.embedding_service import EmbeddingService


class VectorSearchService:
    def __init__(self, db):
        self.db = db
        self.embedder = EmbeddingService()

    def search(self, query: str, top_k: int = 3):
        logger.info(f"Vector search started | query={query} | top_k={top_k}")

        query_vector = self.embedder.embed_text(query)

        logger.info("Query embedding generated for vector search")

        results = (
            self.db.query(DocumentChunk)
            .order_by(DocumentChunk.embedding.cosine_distance(query_vector))
            .limit(top_k)
            .all()
        )

        logger.info(f"Vector search completed | results={len(results)}")

        return [
            {
                "id": row.id,
                "chunk_text": row.chunk_text
            }
            for row in results
        ]