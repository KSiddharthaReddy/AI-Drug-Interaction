from py2neo import Graph
import pandas as pd

# 1) CONNECT TO NEO4J
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Kfbeosc143"  # change this

graph = Graph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def export_training_data():
    # 2) CYPHER QUERY TO GET INTERACTIONS WITH DRUG CLASSES
    query = """
    MATCH (d1:Drug)-[r:INTERACTS_WITH]->(d2:Drug)
    RETURN d1.drug_id AS drug1_id,
           d1.drug_class AS class1,
           d2.drug_id AS drug2_id,
           d2.drug_class AS class2,
           r.severity AS severity
    """
    data = graph.run(query).to_data_frame()
    print("Rows exported:", len(data))
    print(data.head())

    # 3) DROP ROWS WITH MISSING KEY FIELDS
    data = data.dropna(subset=["drug1_id", "drug2_id", "severity"])

    # 4) SAVE TO CSV FOR ML
    data.to_csv("../data_processed/training_data.csv", index=False)
    print("Saved training data to ../data_processed/training_data.csv")

if __name__ == "__main__":
    export_training_data()
