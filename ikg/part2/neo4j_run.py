from neo4j import GraphDatabase
import pandas as pd
from dotenv import load_dotenv
import os
load_dotenv()

# Configuration
uri = "bolt://localhost:7687"  # or your Neo4j URI
user = os.getenv('NEO4J_USER')
password = os.getenv('NEO4J_PASSWORD')
# Path to your triples CSV
triples_csv = r'D:\Scrapping\twitter_scrapping\ikg\part2\triples_output_grouped.csv'

# Load triples into DataFrame
df = pd.read_csv(triples_csv)

class Neo4jHandler:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def insert_triple(self, subject, relation, obj):
        # Use MERGE so you don’t duplicate nodes
        query = (
            "MERGE (a:Entity {name: $subject}) "
            "MERGE (b:Entity {name: $obj}) "
            "MERGE (a)-[r:REL {type: $relation}]->(b) "
            
            "RETURN a, r, b"
        )
        with self.driver.session() as session:
            session.run(query, subject=subject, relation=relation, obj=obj)

    def load_from_df(self, df):
        for _, row in df.iterrows():
            subj = str(row['subject'])
            rel = str(row['predicate'])
            obj = str(row['object'])
            self.insert_triple(subj, rel, obj)

def main():
    handler = Neo4jHandler(uri, user, password)
    handler.load_from_df(df)
    handler.close()
    print("Import into Neo4j done.")

if __name__ == "__main__":
    main()



# http://localhost:7474/browser/ 
# MATCH (n)-[r]->(m)
# RETURN n, r, m