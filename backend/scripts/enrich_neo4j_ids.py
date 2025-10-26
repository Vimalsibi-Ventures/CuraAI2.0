# backend/scripts/enrich_neo4j_ids.py
import os
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase
import re

# --- Load .env from project root ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH)

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASS = os.getenv("NEO4J_PASS")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

# --- Normalize ID function per models.py contract ---
def normalize_id(text: str) -> str:
    if not text:
        return "empty"
    text = text.lower()
    text = text.replace("(", "").replace(")", "")
    text = re.sub(r"[^a-z0-9\- ]", "", text)  # keep alphanumeric & hyphen only
    text = text.replace(" ", "_")
    text = text.strip("_")
    return text or "empty"

# --- Enrich Neo4j nodes ---
def enrich_nodes():
    query = "MATCH (n) RETURN id(n) AS nid, n.name AS name"
    with driver.session() as session:
        results = session.run(query)
        for record in results:
            nid = record["nid"]
            name = record["name"]
            normalized = normalize_id(name)
            session.run(
                "MATCH (n) WHERE id(n)=$nid SET n.normalized_id=$normalized",
                nid=nid,
                normalized=normalized,
            )
    print("Neo4j nodes enriched successfully.")

if __name__ == "__main__":
    enrich_nodes()
