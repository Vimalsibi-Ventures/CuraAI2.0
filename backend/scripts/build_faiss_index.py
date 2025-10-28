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
OUTPUT_DIR = PROJECT_ROOT / "backend" / "storage" / "faiss_llamaindex_storage"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Embedding Model Setup (LOCAL MODEL FOR BUILD SCRIPT) ---
try:
    EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME)
    EXPECTED_DIMENSION = 384
    logger.info(f"Using Local HuggingFace Embedding model ({EMBEDDING_MODEL_NAME}).")
except Exception as e:
    logger.error(f"Failed to initialize local embedding model: {e}", exc_info=True)
    raise SystemExit("Embedding model configuration failed.")

# --- Helper functions ---
def normalize_id(text, prefix):
    # Ensure this EXACTLY matches the function used in enrich_neo4j_ids.py
    original_text = str(text)
    text = str(text).strip().lower()
    text = re.sub(r'\s*\(.*\)\s*', '', text)
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', '_', text)
    text = text.strip('_')
    if not text:
        logger.warning(f"Generated empty ID for prefix '{prefix}' and original text '{original_text}'. Creating fallback ID.")
        fallback_hash = hashlib.md5(original_text.encode()).hexdigest()[:8]
        text = f"unnamed_{fallback_hash}"
    return f"{prefix}:{text}"

def load_json_data(filename, entity_type, name_field):
    path = INPUT_DIR / filename
    logger.info(f"Loading entity data from {path}...")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        # Check if data is a list, if not, maybe it's a single object? Adapt if needed.
        if not isinstance(data, list):
             logger.warning(f"Data in {filename} is not a list. Attempting to process as single object.")
             data = [data] # Wrap in a list

        for item in data:
             # Ensure item is a dictionary before proceeding
            if isinstance(item, dict):
                item["type"] = entity_type
                item["original_name"] = item.get(name_field, "") # Store original name
                count += 1
            else:
                logger.warning(f"Skipping non-dictionary item in {filename}: {item}")

        logger.info(f"Loaded {count} items of type '{entity_type}'.")
        return data
    except FileNotFoundError:
        logger.error(f"Error: File not found at {path}")
        return []
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {path}")
        return []
    except Exception as e:
         logger.error(f"An unexpected error occurred loading {path}: {e}")
         return []

# --- Chunking/Document Creation (Processes FAQs WITHIN entities) ---
def create_llama_documents(entities):
    documents = []
    logger.info(f"Creating LlamaIndex Documents from {len(entities)} entities...")
    processed_count = 0
    skipped_count = 0

    for item in entities:
        # Check if item is a dictionary
        if not isinstance(item, dict):
            logger.warning(f"Skipping non-dictionary entity: {item}")
            skipped_count += 1
            continue

        original_name = item.get("original_name", "")
        item_type = item.get("type", "unknown")

        if not original_name:
            logger.warning(f"Skipping item due to missing name/identifier: {item.get('url', 'Unknown URL')}")
            skipped_count +=1
            continue

        try:
            base_id = normalize_id(original_name, item_type)
            url = item.get("url", "")
            common_metadata = {'name': original_name, 'url': url, 'entity_type': item_type}

            # Create Document for the Name itself
            name_id = base_id
            documents.append(Document(
                text=original_name,
                doc_id=name_id,
                metadata={**common_metadata, 'type': 'name', 'doc_id': name_id}
            ))

            # Create Documents for Text Fields
            for field in ["overview", "symptoms", "causes", "treatments", "prevention", "risk_factors", "complications"]:
                val = item.get(field)
                if not val: continue
                if isinstance(val, list): val = " ".join(filter(None, val)) # Join list items safely

                # Ensure val is a string before regex
                val_str = str(val)
                cleaned_text = re.sub(r'\s+', ' ', val_str).strip()
                # Basic cleaning (add more specific regex if needed)
                cleaned_text = re.sub(r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+\w+\s+\d{1,2},\s+\d{4}\b', '', cleaned_text)
                cleaned_text = re.sub(r'\b(?:Symptoms & causes|Diagnosis & treatment|Diseases & Conditions)\b', '', cleaned_text, flags=re.IGNORECASE)
                cleaned_text = re.sub(r';\s*;*', '; ', cleaned_text).strip('; ')
                cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

                if cleaned_text:
                    chunk_id = f"{base_id}:{field}"
                    context_prefix = field.replace('_',' ').title() + ": "
                    documents.append(Document(
                        text=context_prefix + cleaned_text,
                        doc_id=chunk_id,
                        metadata={**common_metadata, 'type': field, 'doc_id': chunk_id}
                    ))

            # Create Documents for Entity-Specific FAQs (Handles FAQs inside diseases/tests/drugs)
            faqs = item.get("faqs", [])
            if isinstance(faqs, list): # Ensure faqs is a list
                for i, faq in enumerate(faqs):
                    # Ensure faq is a dictionary
                    if isinstance(faq, dict):
                        q = faq.get("question", "").strip()
                        a = faq.get("answer", "").strip()
                        if q and a:
                            text = f"Question: {q} Answer: {a}"
                            chunk_id = f"{base_id}:faq:{i}"
                            documents.append(Document(
                                text=text,
                                doc_id=chunk_id,
                                metadata={**common_metadata, 'type': 'faq', 'doc_id': chunk_id}
                            ))
                    else:
                        logger.warning(f"Skipping non-dictionary FAQ item within '{original_name}': {faq}")
            elif faqs: # Log if 'faqs' exists but isn't a list
                 logger.warning(f"'faqs' field in '{original_name}' is not a list: {type(faqs)}")

            processed_count += 1 # Count processed entity

        except Exception as e:
            logger.error(f"Error processing item '{original_name}': {e}", exc_info=True)
            skipped_count += 1

    logger.info(f"Created {len(documents)} LlamaIndex Documents from {processed_count} entities. Skipped {skipped_count} items.")
    return documents

# --- Build and Persist LlamaIndex (Function remains the same) ---
def build_and_persist_llamaindex(documents, persist_dir=OUTPUT_DIR):
    if not documents:
        logger.error("No documents provided to build index.")
        raise SystemExit("No documents generated for indexing.")

    logger.info(f"Initializing FAISS vector store with expected dimension {EXPECTED_DIMENSION}...")
    faiss_index = faiss.IndexFlatL2(EXPECTED_DIMENSION)
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    logger.info(f"Building VectorStoreIndex with {len(documents)} documents (using local embed model)...")
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True#,
        #embed_batch_size=16
    )

    logger.info(f"Persisting index to directory: {persist_dir}")
    os.makedirs(persist_dir, exist_ok=True)
    index.storage_context.persist(persist_dir=persist_dir)
    logger.info(f"LlamaIndex FAISS index persisted successfully to {persist_dir}.")

# --- Main Execution (Simplified) ---
if __name__ == "__main__":
    logger.info("Starting FAISS index build process using LOCAL embeddings...")

    # Load entities (These should contain the FAQs internally)
    diseases = load_json_data("mayo_all_structured.json", "disease", "disease_name")
    tests = load_json_data("mayo_tests_all_structured.json", "test", "test_name") # Adjust name_field if needed
    drugs = load_json_data("mayo_drugs_structured.json", "drug", "drug_name") # Adjust name_field if needed

    # Combine ONLY the main entity lists
    all_entities = diseases + tests + drugs
    if not all_entities:
         raise SystemExit("No entities loaded from primary JSON files. Check 'data' directory and filenames.")

    # Create LlamaIndex Documents (processes FAQs within entities)
    documents = create_llama_documents(all_entities)

    # Build and save
    build_and_persist_llamaindex(documents)

    logger.info("FAISS index build process completed.")