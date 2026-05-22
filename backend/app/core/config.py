from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    NEO4J_DATABASE: str
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_FROM: str
    SMTP_SERVER: str
    SMTP_PORT: int

    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"
    EMBED_MODEL: str = "nomic-embed-text"

    TOP_K: int = 5
    CHUNK_SIZE: int = 1000

    @property
    def smtp_username(self):
        return self.SMTP_USERNAME

    @property
    def smtp_password(self):
        return self.SMTP_PASSWORD

    @property
    def smtp_from(self):
        return self.SMTP_FROM

    @property
    def smtp_server(self):
        return self.SMTP_SERVER

    @property
    def smtp_port(self):
        return self.SMTP_PORT

    class Config:
        env_file = ".env"


settings = Settings()
