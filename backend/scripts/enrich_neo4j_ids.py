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
# Set logging level to DEBUG to get more detailed output
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Paths ---
logger.debug("Defining script paths...") # DEBUG
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR._parent.parent
INPUT_DIR = PROJECT_ROOT / "backend" / "data"
OUTPUT_DIR = PROJECT_ROOT / "backend" / "storage"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FAISS_INDEX_FILE = OUTPUT_DIR / "vector_index.faiss" # Raw FAISS binary index
DOC_METADATA_FILE = OUTPUT_DIR / "vector_metadata.json" # Our simple metadata map
logger.debug(f"Input Dir: {INPUT_DIR}, Output Dir: {OUTPUT_DIR}") # DEBUG

# --- Embedding Model Setup (LOCAL MODEL FOR BUILD SCRIPT) ---
logger.info("--- Starting Embedding Model Setup ---") # DEBUG
try:
    EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    logger.info(f"Attempting to initialize HuggingFaceEmbedding with model: {EMBEDDING_MODEL_NAME}...") # DEBUG
    # This line might trigger download/caching on first run
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME)
    EXPECTED_DIMENSION = 384
    logger.info(f"Successfully initialized and set Settings.embed_model.") # DEBUG
except Exception as e:
    logger.error(f"Failed to initialize local embedding model: {e}", exc_info=True)
    raise SystemExit("Embedding model configuration failed.")
logger.info("--- Finished Embedding Model Setup ---") # DEBUG

# --- Helper functions ---
def normalize_id(text, prefix):
    # (Keep the same robust normalize_id function)
    original_text = str(text); text = str(text).strip().lower()
    text = re.sub(r'\s*\(.\)\s', '', text); text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', '', text); text = text.strip('')
    if not text:
        logger.warning(f"Generated empty ID for prefix '{prefix}' and original text '{original_text}'. Creating fallback ID.")
        fallback_hash = hashlib.md5(original_text.encode()).hexdigest()[:8]
        text = f"unnamed_{fallback_hash}"
    return f"{prefix}:{text}"

def load_json_data(filename, entity_type, name_field):
    path = INPUT_DIR / filename
    logger.info(f"Attempting to load entity data from {path}...") # DEBUG
    try:
        with open(path, "r", encoding="utf-8") as f: data = json.load(f)
        logger.debug(f"Successfully read JSON from {path}") # DEBUG
        count = 0
        if not isinstance(data, list): data = [data]
        logger.debug(f"Processing {len(data)} potential items from {filename}...") # DEBUG
        for i, item in enumerate(data):
            if isinstance(item, dict):
                item["type"] = entity_type
                item["original_name"] = item.get(name_field, "")
                count += 1
            else:
                logger.warning(f"Skipping non-dictionary item #{i} in {filename}: {str(item)[:100]}...") # Log snippet
        logger.info(f"Loaded {count} items of type '{entity_type}' from {filename}.")
        return data
    except FileNotFoundError: logger.error(f"Error: File not found at {path}"); return []
    except json.JSONDecodeError as e: logger.error(f"Error decoding JSON from {path}: {e}"); return []
    except Exception as e: logger.error(f"An unexpected error occurred loading {path}: {e}"); return []

def create_llama_documents(entities):
    documents = []
    logger.info(f"Starting creation of LlamaIndex Documents from {len(entities)} entities...") # DEBUG
    processed_count = 0; skipped_count = 0
    for item_index, item in enumerate(entities): # Added index for logging
        logger.debug(f"Processing entity #{item_index}...") # DEBUG
        if not isinstance(item, dict):
            logger.warning(f"Skipping entity #{item_index} as it's not a dictionary.") # DEBUG
            skipped_count += 1; continue
        original_name = item.get("original_name", ""); item_type = item.get("type", "unknown")
        if not original_name:
            logger.warning(f"Skipping entity #{item_index} due to missing name.") # DEBUG
            skipped_count +=1; continue
        try:
            base_id = normalize_id(original_name, item_type); url = item.get("url", "")
            common_metadata = {'name': original_name, 'url': url, 'entity_type': item_type}
            logger.debug(f"  Base ID: {base_id}, Type: {item_type}") # DEBUG

            # Create Document for the Name itself
            name_id = base_id
            documents.append(Document(text=original_name, doc_id=name_id, metadata={**common_metadata, 'type': 'name', 'doc_id': name_id}))
            logger.debug(f"    Added 'name' chunk.") # DEBUG

            # Create Documents for Text Fields
            for field in ["overview", "symptoms", "causes", "treatments", "prevention", "risk_factors", "complications"]:
                val = item.get(field)
                if not val: continue
                if isinstance(val, list): val = " ".join(filter(None, val))
                val_str = str(val); cleaned_text = re.sub(r'\s+', ' ', val_str).strip()
                # Basic cleaning (add more specific regex if needed)
                cleaned_text = re.sub(r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+\w+\s+\d{1,2},\s+\d{4}\b', '', cleaned_text)
                cleaned_text = re.sub(r'\b(?:Symptoms & causes|Diagnosis & treatment|Diseases & Conditions)\b', '', cleaned_text, flags=re.IGNORECASE)
                cleaned_text = re.sub(r';\s*;*', '; ', cleaned_text).strip('; '); cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
                if cleaned_text:
                    chunk_id = f"{base_id}:{field}"; context_prefix = field.replace('_',' ').title() + ": "
                    documents.append(Document(text=context_prefix + cleaned_text, doc_id=chunk_id, metadata={**common_metadata, 'type': field, 'doc_id': chunk_id}))
                    logger.debug(f"    Added '{field}' chunk.") # DEBUG

            # Create Documents for Entity-Specific FAQs
            faqs = item.get("faqs", [])
            if isinstance(faqs, list):
                logger.debug(f"    Processing {len(faqs)} FAQs for this entity...") # DEBUG
                for i, faq in enumerate(faqs):
                    if isinstance(faq, dict):
                        q = faq.get("question", "").strip(); a = faq.get("answer", "").strip()
                        if q and a:
                            text = f"Question: {q} Answer: {a}"; chunk_id = f"{base_id}:faq:{i}"
                            documents.append(Document(text=text, doc_id=chunk_id, metadata={**common_metadata, 'type': 'faq', 'doc_id': chunk_id}))
                            logger.debug(f"      Added 'faq:{i}' chunk.") # DEBUG
                    else: logger.warning(f"    Skipping non-dictionary FAQ item #{i} within '{original_name}': {str(faq)[:100]}...")
            elif faqs: logger.warning(f"  'faqs' field in '{original_name}' is not a list: {type(faqs)}")
            processed_count += 1
        except Exception as e:
            logger.error(f"Error processing item #{item_index} ('{original_name}'): {e}", exc_info=True)
            skipped_count += 1
            # Decide if you want to continue or stop on error
            # raise e # Uncomment to stop on first error

    logger.info(f"Finished creating {len(documents)} LlamaIndex Documents from {processed_count} entities. Skipped {skipped_count} items.") # DEBUG
    return documents

# --- Build FAISS Index and Save Manually ---
def build_and_save_manual(documents, index_path=FAISS_INDEX_FILE, metadata_path=DOC_METADATA_FILE):
    if not documents: logger.error("No documents provided..."); raise SystemExit(...)
    embed_model = Settings.embed_model
    if not embed_model: raise SystemExit("Embedding model not configured...")

    logger.info(f"Starting embedding generation for {len(documents)} documents...") # DEBUG
    texts_to_embed = [doc.get_content() for doc in documents]
    embeddings = embed_model.get_text_embedding_batch(texts_to_embed, show_progress=True)
    logger.info("Finished generating embeddings.") # DEBUG
    vectors = np.array(embeddings).astype("float32")
    logger.debug(f"Generated vectors of shape: {vectors.shape}") # DEBUG

    if vectors.shape[1] != EXPECTED_DIMENSION:
        logger.error(f"Embedding dimension mismatch! Expected {EXPECTED_DIMENSION}, got {vectors.shape[1]}.")
        raise SystemExit("Embedding dimension error.")

    logger.info(f"Building FAISS index (IndexFlatL2 + IndexIDMap)...") # DEBUG
    faiss_index = faiss.IndexFlatL2(EXPECTED_DIMENSION)
    faiss_ids = np.arange(len(vectors))
    index_mapped = faiss.IndexIDMap(faiss_index)
    logger.debug("Attempting to add vectors to FAISS index...") # DEBUG
    index_mapped.add_with_ids(vectors, faiss_ids)
    logger.info(f"Successfully added {index_mapped.ntotal} vectors to FAISS index.") # DEBUG

    logger.info(f"Attempting to save FAISS index to {index_path}...") # DEBUG
    faiss.write_index(index_mapped, str(index_path)) # Use faiss function
    logger.info("FAISS index saved successfully.")

    # --- Create and Save Metadata Map ---
    logger.info(f"Creating metadata map for {len(documents)} documents...") # DEBUG
    metadata_map = {}
    for i, doc in enumerate(documents):
        faiss_id = i # The sequential ID used in add_with_ids
        metadata_map[str(faiss_id)] = {
            "doc_id": doc.doc_id,
            "text": doc.text,
            "metadata": doc.metadata
        }
    logger.debug(f"Finished creating metadata map with {len(metadata_map)} entries.") # DEBUG

    logger.info(f"Attempting to save metadata map to {metadata_path}...") # DEBUG
    try:
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata_map, f, indent=2, ensure_ascii=False)
        logger.info("Metadata map saved successfully.")
    except Exception as e:
        logger.error(f"Failed to save metadata map: {e}", exc_info=True)
        raise SystemExit("Metadata saving failed.")
    logger.info("Finished building and saving index/metadata.") # DEBUG


# --- Main Execution ---
if __name__ == "_main_":
    logger.info("--- Starting FAISS index build process (Manual Save) ---") # DEBUG

    logger.info("Step 1: Loading entities...")
    diseases = load_json_data("mayo_all_structured.json", "disease", "disease_name")
    tests = load_json_data("mayo_tests_all_structured.json", "test", "test_name")
    drugs = load_json_data("mayo_drugs_structured.json", "drug", "drug_name")
    all_entities = diseases + tests + drugs
    if not all_entities:
         logger.error("No entities were loaded. Exiting.")
         raise SystemExit("No entities loaded.")
    logger.info(f"Step 1 Completed: Loaded a total of {len(all_entities)} entities.")

    logger.info("Step 2: Creating LlamaIndex documents...")
    documents = create_llama_documents(all_entities)
    if not documents:
         logger.error("No documents were created from entities. Exiting.")
         raise SystemExit("No documents created.")
    logger.info(f"Step 2 Completed: Created {len(documents)} documents.")

    logger.info("Step 3: Building FAISS index and saving manually...")
    build_and_save_manual(documents)
    logger.info("Step 3 Completed: Index and metadata saved.")

    logger.info("--- FAISS index build process completed successfully (Manual Save) ---") # DEBUG