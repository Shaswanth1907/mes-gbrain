import requests

from app.core.config import settings
from app.core.logger import logger


class EmbeddingService:
    def embed_text(self, text: str):
        logger.info(f"Embedding request started | chars={len(text)}")

        response = requests.post(
            f"{settings.OLLAMA_URL}/api/embeddings",
            json={
                "model": settings.EMBED_MODEL,
                "prompt": text
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()
        embedding = data["embedding"]

        logger.info(f"Embedding generated | dimensions={len(embedding)}")

        return embedding

    def embed_batch(self, texts: list[str]):
        logger.info(f"Batch embedding started | count={len(texts)}")

        embeddings = []

        for index, text in enumerate(texts, start=1):
            logger.info(f"Batch embedding item | item={index}/{len(texts)}")
            vector = self.embed_text(text)
            embeddings.append(vector)

        logger.info(f"Batch embedding completed | count={len(embeddings)}")

        return embeddings