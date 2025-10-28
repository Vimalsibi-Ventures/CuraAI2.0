import os
import json
import logging
from pathlib import Path
import faiss # Only need faiss and numpy here
import numpy as np

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Paths ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
# Input: Where generate_embeddings.py saved its output
TEMP_INPUT_DIR = PROJECT_ROOT / "backend" / "storage" / "temp_embeddings"
VECTORS_FILE = TEMP_INPUT_DIR / "embeddings.npy"
DOCUMENTS_FILE = TEMP_INPUT_DIR / "documents_with_ids.json"
# Output: Final files for main.py
OUTPUT_DIR = PROJECT_ROOT / "backend" / "storage"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FAISS_INDEX_FILE = OUTPUT_DIR / "vector_index.faiss"
DOC_METADATA_FILE = OUTPUT_DIR / "vector_metadata.json"

# --- Dimension (Must match model used in generate_embeddings.py) ---
EXPECTED_DIMENSION = 384 # For all-MiniLM-L6-v2

# --- Main Execution ---
if __name__ == "__main__":
    logger.info("--- Starting Step B: Build FAISS Index from Precomputed Vectors ---")

    # --- Load Precomputed Data ---
    logger.info(f"Step 1: Loading vectors from {VECTORS_FILE}...")
    if not VECTORS_FILE.exists():
        raise SystemExit(f"ERROR: Vectors file not found. Run generate_embeddings.py first: {VECTORS_FILE}")
    try:
        vectors = np.load(VECTORS_FILE)
        logger.info(f"Loaded vectors with shape: {vectors.shape}")
    except Exception as e:
        logger.error(f"Failed to load vectors: {e}", exc_info=True)
        raise SystemExit("Loading vectors failed.")

    logger.info(f"Step 2: Loading document chunks/metadata from {DOCUMENTS_FILE}...")
    if not DOCUMENTS_FILE.exists():
        raise SystemExit(f"ERROR: Documents file not found. Run generate_embeddings.py first: {DOCUMENTS_FILE}")
    try:
        with open(DOCUMENTS_FILE, "r", encoding="utf-8") as f:
            document_chunks = json.load(f) # List of {'doc_id': str, 'text': str, 'metadata': dict}
        logger.info(f"Loaded {len(document_chunks)} document chunks.")
    except Exception as e:
        logger.error(f"Failed to load document chunks: {e}", exc_info=True)
        raise SystemExit("Loading document chunks failed.")

    # --- Validation ---
    if vectors.shape[0] != len(document_chunks):
        raise SystemExit(f"ERROR: Mismatch in vector count ({vectors.shape[0]}) vs document count ({len(document_chunks)}). Files are corrupt or mismatched.")
    if vectors.shape[1] != EXPECTED_DIMENSION:
        raise SystemExit(f"ERROR: Embedding dimension mismatch ({vectors.shape[1]} vs {EXPECTED_DIMENSION})")

    # --- Build FAISS Index ---
    logger.info(f"Step 3: Building FAISS index (IndexFlatL2 + IndexIDMap)...")
    try:
        faiss_index = faiss.IndexFlatL2(EXPECTED_DIMENSION)
        faiss_ids = np.arange(len(vectors)) # Sequential IDs 0, 1, 2...
        index_mapped = faiss.IndexIDMap(faiss_index)
        index_mapped.add_with_ids(vectors.astype('float32'), faiss_ids) # Ensure float32
        logger.info(f"Successfully added {index_mapped.ntotal} vectors to FAISS index.")
    except Exception as e:
        logger.error(f"Failed to build FAISS index object: {e}", exc_info=True)
        raise SystemExit("FAISS index building failed.")

    # --- Save FAISS Index ---
    logger.info(f"Step 4: Saving FAISS index to {FAISS_INDEX_FILE}...")
    try:
        faiss.write_index(index_mapped, str(FAISS_INDEX_FILE))
        logger.info("FAISS index saved successfully.")
    except Exception as e:
        logger.error(f"Failed to save FAISS index file: {e}", exc_info=True)
        raise SystemExit("Saving FAISS index failed.")

    # --- Create and Save Final Metadata Map ---
    logger.info(f"Step 5: Creating final metadata map...")
    final_metadata_map = {}
    try:
        for i, chunk_data in enumerate(document_chunks):
            faiss_id = i # The sequential ID used in add_with_ids
            # Extract required fields for main.py
            final_metadata_map[str(faiss_id)] = {
                "doc_id": chunk_data.get("doc_id", f"missing_id_{i}"),
                "text": chunk_data.get("text", ""), # Store original text for LlamaIndex
                "metadata": chunk_data.get("metadata", {}) # Store LlamaIndex metadata
            }
        logger.info(f"Created metadata map with {len(final_metadata_map)} entries.")
    except Exception as e:
        logger.error(f"Failed during metadata map creation: {e}", exc_info=True)
        raise SystemExit("Metadata map creation failed.")

    logger.info(f"Step 6: Saving metadata map to {DOC_METADATA_FILE}...")
    try:
        with open(DOC_METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(final_metadata_map, f, indent=2, ensure_ascii=False)
        logger.info("Metadata map saved successfully.")
    except Exception as e:
        logger.error(f"Failed to save metadata map: {e}", exc_info=True)
        raise SystemExit("Metadata saving failed.")

    # --- Optional: Clean up temporary files ---
    # logger.info("Cleaning up temporary embedding files...")
    # try:
    #     os.remove(VECTORS_FILE)
    #     os.remove(DOCUMENTS_FILE)
    #     # os.rmdir(TEMP_OUTPUT_DIR) # Only if empty
    #     logger.info("Temporary files removed.")
    # except Exception as e:
    #     logger.warning(f"Could not clean up temporary files: {e}")

    logger.info("--- Step B: FAISS Index Build Completed Successfully ---")