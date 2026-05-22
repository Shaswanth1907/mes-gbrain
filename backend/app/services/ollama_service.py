import requests
from app.core.config import settings


class OllamaService:
    def generate(self, prompt: str):
        return self.generate_response(prompt)

    def generate_response(self, prompt: str):
        try:
            print("=== CALLING OLLAMA ===")
            print(f"URL: {settings.OLLAMA_URL}")
            print(f"MODEL: {settings.OLLAMA_MODEL}")

            response = requests.post(
                f"{settings.OLLAMA_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=180
            )

            print("=== OLLAMA RESPONSE RECEIVED ===")

            response.raise_for_status()

            data = response.json()

            print("=== RESPONSE PARSED ===")

            return data["response"]

        except Exception as e:
            print("OLLAMA ERROR:", str(e))
            raise
