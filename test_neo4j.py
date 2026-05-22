from app.graph.neo4j_client import neo4j_client

with neo4j_client.session() as session:
    result = session.run("""
        CREATE (m:Machine {
            machine_code:'TEST-001',
            name:'Neo4j Test Machine'
        })
        RETURN m
    """)

    print(result.single())
