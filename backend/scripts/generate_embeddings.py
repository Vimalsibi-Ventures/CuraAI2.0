import os
import json
import re
import logging
from pathlib import Path
import numpy as np
import hashlib
import time

# ONLY import embedding model here
from sentence_transformers import SentenceTransformer

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Paths ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
INPUT_DIR = PROJECT_ROOT / "backend" / "data"
# Temporary output for this script
TEMP_OUTPUT_DIR = PROJECT_ROOT / "backend" / "storage" / "temp_embeddings"
TEMP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
VECTORS_FILE = TEMP_OUTPUT_DIR / "embeddings.npy"
DOCUMENTS_FILE = TEMP_OUTPUT_DIR / "documents_with_ids.json" # Store text + metadata needed by next script

# --- Embedding Model ---
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EXPECTED_DIMENSION = 384

# --- Helper functions ---
def normalize_id(text, prefix):
    # (Same robust normalize_id function)
    original_text = str(text); text = str(text).strip().lower()
    text = re.sub(r'\s*\(.\)\s', '', text); text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', '', text); text = text.strip('')
    if not text:
        logger.warning(f"Generated empty ID for prefix '{prefix}' and original text '{original_text}'. Fallback needed.")
        fallback_hash = hashlib.md5(original_text.encode()).hexdigest()[:8]
        text = f"unnamed_{fallback_hash}"
    return f"{prefix}:{text}"

def load_json_data(filename, entity_type, name_field):
    # (Same robust load_json_data function)
    path = INPUT_DIR / filename; logger.info(f"Loading entity data from {path}...")
    try:
        with open(path, "r", encoding="utf-8") as f: data = json.load(f)
        count = 0;
        if not isinstance(data, list): data = [data]
        for item in data:
            if isinstance(item, dict): item["type"] = entity_type; item["original_name"] = item.get(name_field, ""); count += 1
            else: logger.warning(f"Skipping non-dictionary item in {filename}: {str(item)[:100]}...")
        logger.info(f"Loaded {count} items of type '{entity_type}' from {filename}.")
        return data
    except FileNotFoundError: logger.error(f"Error: File not found at {path}"); return []
    except json.JSONDecodeError as e: logger.error(f"Error decoding JSON from {path}: {e}"); return []
    except Exception as e: logger.error(f"An unexpected error occurred loading {path}: {e}"); return []

# --- Chunking Logic (Returns list of dictionaries) ---
def create_document_chunks(entities):
    chunks = [] # List to hold dictionaries: {'doc_id': str, 'text': str, 'metadata': dict}
    logger.info(f"Creating document chunks from {len(entities)} entities...")
    processed_count = 0; skipped_count = 0
    for item_index, item in enumerate(entities):
        if not isinstance(item, dict): skipped_count += 1; continue
        original_name = item.get("original_name", ""); item_type = item.get("type", "unknown")
        if not original_name: skipped_count +=1; continue
        try:
            base_id = normalize_id(original_name, item_type); url = item.get("url", "")
            common_metadata = {'name': original_name, 'url': url, 'entity_type': item_type}

            # Chunk for the Name itself
            name_id = base_id
            chunks.append({
                'doc_id': name_id,
                'text': original_name,
                'metadata': {**common_metadata, 'type': 'name', 'doc_id': name_id}
            })

            # Chunks for Text Fields
            for field in ["overview", "symptoms", "causes", "treatments", "prevention", "risk_factors", "complications"]:
                val = item.get(field)
                if not val: continue
                if isinstance(val, list): val = " ".join(filter(None, val))
                val_str = str(val); cleaned_text = re.sub(r'\s+', ' ', val_str).strip()
                # Basic cleaning
                cleaned_text = re.sub(r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+\w+\s+\d{1,2},\s+\d{4}\b', '', cleaned_text)
                cleaned_text = re.sub(r'\b(?:Symptoms & causes|Diagnosis & treatment|Diseases & Conditions)\b', '', cleaned_text, flags=re.IGNORECASE)
                cleaned_text = re.sub(r';\s*;*', '; ', cleaned_text).strip('; '); cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
                if cleaned_text:
                    chunk_id = f"{base_id}:{field}"; context_prefix = field.replace('_',' ').title() + ": "
                    chunks.append({
                        'doc_id': chunk_id,
                        'text': context_prefix + cleaned_text,
                        'metadata': {**common_metadata, 'type': field, 'doc_id': chunk_id}
                    })

            # Chunks for Entity-Specific FAQs
            faqs = item.get("faqs", [])
            if isinstance(faqs, list):
                for i, faq in enumerate(faqs):
                    if isinstance(faq, dict):
                        q = faq.get("question", "").strip(); a = faq.get("answer", "").strip()
                        if q and a:
                            text = f"Question: {q} Answer: {a}"; chunk_id = f"{base_id}:faq:{i}"
                            chunks.append({
                                'doc_id': chunk_id,
                                'text': text,
                                'metadata': {**common_metadata, 'type': 'faq', 'doc_id': chunk_id}
                            })
                    else: logger.warning(f"Skipping non-dictionary FAQ item within '{original_name}': {str(faq)[:100]}...")
            elif faqs: logger.warning(f"'faqs' field in '{original_name}' is not a list: {type(faqs)}")
            processed_count += 1
        except Exception as e: logger.error(f"Error processing item #{item_index} ('{original_name}'): {e}", exc_info=True); skipped_count += 1
    logger.info(f"Finished creating {len(chunks)} document chunks from {processed_count} entities. Skipped {skipped_count} items.")
    return chunks

# --- Main Execution ---
if __name__ == "__main__":
    logger.info("--- Starting Step A: Embedding Generation ---")

    logger.info("Step 1: Initializing Embedding Model...")
    try:
        # Load model ONCE
        model = SentenceTransformer(EMBEDDING_MODEL_NAME, device='cpu') # Force CPU
        logger.info("Embedding model initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize embedding model: {e}", exc_info=True)
        raise SystemExit("Embedding model init failed.")

    logger.info("Step 2: Loading entities...")
    diseases = load_json_data("mayo_all_structured.json", "disease", "disease_name")
    tests = load_json_data("mayo_tests_all_structured.json", "test", "test_name")
    drugs = load_json_data("mayo_drugs_structured.json", "drug", "drug_name")
    all_entities = diseases + tests + drugs
    if not all_entities: raise SystemExit("No entities loaded.")
    logger.info(f"Step 2 Completed: Loaded {len(all_entities)} entities.")

    logger.info("Step 3: Creating document chunks...")
    document_chunks = create_document_chunks(all_entities) # List of dictionaries
    if not document_chunks: raise SystemExit("No document chunks created.")
    texts_to_embed = [chunk['text'] for chunk in document_chunks]
    logger.info(f"Step 3 Completed: Created {len(document_chunks)} chunks.")

    logger.info(f"Step 4: Generating embeddings for {len(texts_to_embed)} texts (using CPU)...")
    try:
        # Generate embeddings (consider batching if RAM is still an issue, but maybe not needed now)
        start_time = time.time()
        vectors = model.encode(texts_to_embed, show_progress_bar=True, batch_size=32) # Use batches
        end_time = time.time()
        logger.info(f"Embedding generation completed in {end_time - start_time:.2f} seconds.")
        vectors_np = np.array(vectors).astype("float32")
    except Exception as e:
        logger.error(f"Failed during embedding generation: {e}", exc_info=True)
        raise SystemExit("Embedding generation failed.")

    if vectors_np.shape[0] != len(document_chunks):
        raise SystemExit(f"ERROR: Mismatch in vector count ({vectors_np.shape[0]}) vs document count ({len(document_chunks)})")
    if vectors_np.shape[1] != EXPECTED_DIMENSION:
        raise SystemExit(f"ERROR: Embedding dimension mismatch ({vectors_np.shape[1]} vs {EXPECTED_DIMENSION})")

    logger.info(f"Step 5: Saving {vectors_np.shape[0]} vectors to {VECTORS_FILE}...")
    np.save(VECTORS_FILE, vectors_np)
    logger.info("Vectors saved successfully.")

    logger.info(f"Step 6: Saving {len(document_chunks)} document chunks/metadata to {DOCUMENTS_FILE}...")
    try:
        with open(DOCUMENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(document_chunks, f, ensure_ascii=False) # Save the list of chunk dicts
        logger.info("Document chunks saved successfully.")
    except Exception as e:
        logger.error(f"Failed to save document chunks: {e}", exc_info=True)
        raise SystemExit("Saving document chunks failed.")

    logger.info("--- Step A: Embedding Generation Completed Successfully ---")