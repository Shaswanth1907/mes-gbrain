from neo4j import GraphDatabase

from app.config.settings import settings


class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(
                settings.NEO4J_USER,
                settings.NEO4J_PASSWORD
            )
        )

    def session(self):
        return self.driver.session(
            database=settings.NEO4J_DATABASE
        )

    def close(self):
        self.driver.close()


neo4j_client = Neo4jClient()
