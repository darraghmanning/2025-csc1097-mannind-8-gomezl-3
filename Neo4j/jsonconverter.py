import sys
from pathlib import Path
from neo4j import GraphDatabase

# CONFIG: Update this with your actual Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4j"

CYPHER_FILE = Path("create.cypher")
NEO4J_IMPORT_DIR = Path("C:/Users/Darragh/.Neo4jDesktop/relate-data/dbmss/dbms-3f2a8f14-b37f-45b1-9894-1224e2fb5096/import")

if len(sys.argv) < 2:
    print("Usage: python load_study.py your_study.json")
    sys.exit(1)

json_filename = sys.argv[1]
json_path = NEO4J_IMPORT_DIR / json_filename

# if not json_path.exists():
#     print(f"File not found in import directory: {json_path}")
#     sys.exit(1)

if not CYPHER_FILE.exists():
    print(f"Cypher script not found: {CYPHER_FILE}")
    sys.exit(1)

with open(CYPHER_FILE, "r") as f:
    cypher_script = f.read()

cypher_script = cypher_script.replace("file:///default.json", f"file:///{json_filename}")
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
with driver.session() as session:
    session.run(cypher_script)

print(f"Successfully loaded {json_filename} into Neo4j.")