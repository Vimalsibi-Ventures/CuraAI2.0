import os
import json
import re
import logging
from pathlib import Path
import faiss # Still needed
import numpy as np # Still needed
import hashlib # For fallback IDs

# LlamaIndex Imports
from llama_index.core import Document, VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.faiss import FaissVectorStore
# Use LOCAL HuggingFace Embeddings for this build script
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Paths ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
INPUT_DIR = PROJECT_ROOT / "backend" / "data"
# Save outputs directly into backend/storage (individual files)
OUTPUT_DIR = PROJECT_ROOT / "backend" / "storage"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FAISS_INDEX_FILE = OUTPUT_DIR / "vector_index.faiss" # Raw FAISS binary index
DOC_METADATA_FILE = OUTPUT_DIR / "vector_metadata.json" # Our simple metadata map

# --- Embedding Model Setup (LOCAL MODEL FOR BUILD SCRIPT) ---
try:
    EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME)
    EXPECTED_DIMENSION = 384
    logger.info(f"Using Local HuggingFace Embedding model ({EMBEDDING_MODEL_NAME}).")
except Exception as e:
    logger.error(f"Failed to initialize local embedding model: {e}", exc_info=True)
    raise SystemExit("Embedding model configuration failed.")

# --- Helper functions (normalize_id, load_json_data remain the same) ---
def normalize_id(text, prefix):
    # (Keep the same robust normalize_id function from previous versions)
    original_text = str(text) # Keep original for fallback
    text = str(text).strip().lower()
    text = re.sub(r'\s*\(.\)\s', '', text) # Remove content in parentheses
    text = re.sub(r'[^\w\s-]', '', text) # Keep alphanumeric, spaces, hyphens
    text = re.sub(r'\s+', '_', text) # Replace spaces with underscores
    text = text.strip('_') # Remove leading/trailing underscores
    if not text:
        logger.warning(f"Generated empty ID for prefix '{prefix}' and original text '{original_text}'. Creating fallback ID.")
        fallback_hash = hashlib.md5(original_text.encode()).hexdigest()[:8]
        text = f"unnamed_{fallback_hash}"
    return f"{prefix}:{text}"

def load_json_data(filename, entity_type, name_field):
    # (Keep the same robust load_json_data function)
    path = INPUT_DIR / filename
    logger.info(f"Loading entity data from {path}...")
    try:
        with open(path, "r", encoding="utf-8") as f: data = json.load(f)
        count = 0
        if not isinstance(data, list): data = [data]
        for item in data:
            if isinstance(item, dict):
                item["type"] = entity_type
                item["original_name"] = item.get(name_field, "")
                count += 1
            else: logger.warning(f"Skipping non-dictionary item in {filename}: {item}")
        logger.info(f"Loaded {count} items of type '{entity_type}'.")
        return data
    except FileNotFoundError: logger.error(f"Error: File not found at {path}"); return []
    except json.JSONDecodeError: logger.error(f"Error decoding JSON from {path}"); return []
    except Exception as e: logger.error(f"An unexpected error occurred loading {path}: {e}"); return []

# --- Chunking/Document Creation (Function remains the same) ---
def create_llama_documents(entities):
    # (Keep the same robust create_llama_documents function creating LlamaIndex Document objects)
    documents = []
    logger.info(f"Creating LlamaIndex Documents from {len(entities)} entities...")
    processed_count = 0; skipped_count = 0
    for item in entities:
        if not isinstance(item, dict): skipped_count += 1; continue
        original_name = item.get("original_name", ""); item_type = item.get("type", "unknown")
        if not original_name: skipped_count +=1; continue
        try:
            base_id = normalize_id(original_name, item_type); url = item.get("url", "")
            common_metadata = {'name': original_name, 'url': url, 'entity_type': item_type}
            name_id = base_id
            documents.append(Document(text=original_name, doc_id=name_id, metadata={**common_metadata, 'type': 'name', 'doc_id': name_id}))
            for field in ["overview", "symptoms", "causes", "treatments", "prevention", "risk_factors", "complications"]:
                val = item.get(field)
                if not val: continue
                if isinstance(val, list): val = " ".join(filter(None, val))
                val_str = str(val); cleaned_text = re.sub(r'\s+', ' ', val_str).strip()
                cleaned_text = re.sub(r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+\w+\s+\d{1,2},\s+\d{4}\b', '', cleaned_text)
                cleaned_text = re.sub(r'\b(?:Symptoms & causes|Diagnosis & treatment|Diseases & Conditions)\b', '', cleaned_text, flags=re.IGNORECASE)
                cleaned_text = re.sub(r';\s*;*', '; ', cleaned_text).strip('; '); cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
                if cleaned_text:
                    chunk_id = f"{base_id}:{field}"; context_prefix = field.replace('_',' ').title() + ": "
                    documents.append(Document(text=context_prefix + cleaned_text, doc_id=chunk_id, metadata={**common_metadata, 'type': field, 'doc_id': chunk_id}))
            faqs = item.get("faqs", [])
            if isinstance(faqs, list):
                for i, faq in enumerate(faqs):
                    if isinstance(faq, dict):
                        q = faq.get("question", "").strip(); a = faq.get("answer", "").strip()
                        if q and a:
                            text = f"Question: {q} Answer: {a}"; chunk_id = f"{base_id}:faq:{i}"
                            documents.append(Document(text=text, doc_id=chunk_id, metadata={**common_metadata, 'type': 'faq', 'doc_id': chunk_id}))
                    else: logger.warning(f"Skipping non-dictionary FAQ item within '{original_name}': {faq}")
            elif faqs: logger.warning(f"'faqs' field in '{original_name}' is not a list: {type(faqs)}")
            processed_count += 1
        except Exception as e: logger.error(f"Error processing item '{original_name}': {e}", exc_info=True); skipped_count += 1
    logger.info(f"Created {len(documents)} LlamaIndex Documents from {processed_count} entities. Skipped {skipped_count} items.")
    return documents

# --- Build FAISS Index and Save Manually ---
def build_and_save_manual(documents, index_path=FAISS_INDEX_FILE, metadata_path=DOC_METADATA_FILE):
    if not documents:
        logger.error("No documents provided to build index.")
        raise SystemExit("No documents generated for indexing.")

    embed_model = Settings.embed_model # Get the globally set embed model
    if not embed_model:
        raise SystemExit("Embedding model not configured in LlamaIndex Settings.")

    logger.info(f"Generating embeddings for {len(documents)} documents...")
    texts_to_embed = [doc.get_content() for doc in documents]
    # Generate embeddings in batches to potentially manage memory
    embeddings = embed_model.get_text_embedding_batch(texts_to_embed, show_progress=True)
    vectors = np.array(embeddings).astype("float32")

    if vectors.shape[1] != EXPECTED_DIMENSION:
        logger.error(f"Embedding dimension mismatch! Expected {EXPECTED_DIMENSION}, got {vectors.shape[1]}.")
        raise SystemExit("Embedding dimension error.")

    logger.info(f"Building FAISS index (IndexFlatL2)...")
    faiss_index = faiss.IndexFlatL2(EXPECTED_DIMENSION)
    # We need sequential integer IDs (0, 1, 2...) for FAISS IndexIDMap
    faiss_ids = np.arange(len(vectors))
    index_mapped = faiss.IndexIDMap(faiss_index)
    index_mapped.add_with_ids(vectors, faiss_ids)

    logger.info(f"Saving FAISS index to {index_path}...")
    faiss.write_index(index_mapped, str(index_path)) # Use faiss function
    logger.info("FAISS index saved successfully.")

    # --- Create and Save Metadata Map ---
    logger.info(f"Creating metadata map...")
    metadata_map = {}
    for i, doc in enumerate(documents):
        faiss_id = i # The sequential ID used in add_with_ids
        metadata_map[str(faiss_id)] = {
            "doc_id": doc.doc_id, # The meaningful ID (e.g., disease:avnrt:overview)
            "text": doc.text, # Store the original text!
            "metadata": doc.metadata # Store the LlamaIndex metadata dict
        }

    logger.info(f"Saving metadata map to {metadata_path}...")
    try:
        with open(metadata_path, "w", encoding="utf-8") as f:
             # Ensure_ascii=False is important for non-English chars if any
            json.dump(metadata_map, f, indent=2, ensure_ascii=False)
        logger.info("Metadata map saved successfully.")
    except Exception as e:
        logger.error(f"Failed to save metadata map: {e}", exc_info=True)
        raise SystemExit("Metadata saving failed.")


# --- Main Execution ---
if __name__ == "_main_":
    logger.info("Starting FAISS index build process using LOCAL embeddings (Manual Save)...")

    # Load entities
    diseases = load_json_data("mayo_all_structured.json", "disease", "disease_name")
    tests = load_json_data("mayo_tests_all_structured.json", "test", "test_name")
    drugs = load_json_data("mayo_drugs_structured.json", "drug", "drug_name")
    all_entities = diseases + tests + drugs
    if not all_entities:
         raise SystemExit("No entities loaded.")

    # Create LlamaIndex Document objects
    documents = create_llama_documents(all_entities)

    # Build index and save manually
    build_and_save_manual(documents)

    logger.info("FAISS index build process completed (Manual Save).")