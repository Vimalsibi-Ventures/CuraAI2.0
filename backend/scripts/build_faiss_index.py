# backend/scripts/build_faiss_index.py
import os
import json
from pathlib import Path
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore
import faiss
import re

# --- Paths ---
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_DIR = SCRIPT_DIR.parent / "storage" / "faiss_llamaindex_storage"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Embedding ---
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
EXPECTED_DIMENSION = 384

# --- Normalize ID (same as enrich script) ---
def normalize_id(text: str) -> str:
    if not text:
        return "empty"
    text = text.lower()
    text = text.replace("(", "").replace(")", "")
    text = re.sub(r"[^a-z0-9\- ]", "", text)
    text = text.replace(" ", "_")
    text = text.strip("_")
    return text or "empty"

# --- Load JSON files ---
documents = []
for json_file in DATA_DIR.glob("*.json"):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        for item in data:
            metadata = {
                "id": normalize_id(item.get("id", "")),
                "name": item.get("name"),
                "url": item.get("url"),
                "type": item.get("type"),
            }
            doc = Document(text=item.get("text", ""), metadata=metadata)
            documents.append(doc)

# --- Create FAISS index ---
index_flat = faiss.IndexFlatL2(EXPECTED_DIMENSION)
vector_store = FaissVectorStore(index=index_flat, embedding=embed_model)

storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

# --- Persist index ---
storage_context.persist(persist_dir=OUTPUT_DIR)
print(f"FAISS index built and saved to {OUTPUT_DIR}")
