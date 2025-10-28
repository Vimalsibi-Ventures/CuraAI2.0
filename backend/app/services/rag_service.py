import os
import json
import logging
from pathlib import Path
from typing import Tuple, Optional, List, Dict, Any
import faiss # Needed for manual load
import numpy as np # Needed for manual load
import hashlib # For fallback IDs

# LlamaIndex Imports
from llama_index.core import (
    Settings,
    StorageContext,
    KnowledgeGraphIndex,
    VectorStoreIndex
)
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.tools import QueryEngineTool
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core.schema import TextNode # Needed to reconstruct nodes

logger = logging.getLogger(__name__)

# --- Paths for MANUALLY SAVED files ---
SCRIPT_DIR = Path(__file__).resolve().parent
STORAGE_DIR = SCRIPT_DIR.parent.parent / "storage" # Go up services -> app -> backend -> storage
FAISS_INDEX_FILE_PATH = STORAGE_DIR / "vector_index.faiss" # Path to manual FAISS index
DOC_METADATA_FILE_PATH = STORAGE_DIR / "vector_metadata.json" # Path to manual metadata

def load_rag_engines() -> Tuple[Optional[VectorStoreIndex], Optional[KnowledgeGraphIndex]]:
    """
    Load RAG engines: FAISS vector index (from MANUALLY saved files)
    and initialize Neo4j KG index connection.
    Returns tuple of (vector_index, kg_index)
    """
    vector_index = None
    kg_index = None # Start as None
    logger.info("Attempting to load RAG engines...")

    # --- Load Local Embedding Model ---
    # Must match the model used in build_faiss_index.py
    try:
        embed_model = HuggingFaceEmbedding(model_name='sentence-transformers/all-MiniLM-L6-v2', device='cpu')
        Settings.embed_model = embed_model
        logger.info("Local embedding model loaded and set in Settings.")
    except Exception as e:
        logger.error(f"CRITICAL: Failed to load local embedding model: {e}", exc_info=True)
        return None, None # Fail early

    # --- Load FAISS Vector Index (MANUAL LOAD METHOD) ---
    logger.info("Attempting to load FAISS index and metadata from manual files...")
    vector_store = None # Initialize vector_store
    doc_metadata = {}   # Initialize metadata store

    if FAISS_INDEX_FILE_PATH.exists() and DOC_METADATA_FILE_PATH.exists():
        try:
            logger.info(f"Loading FAISS index from {FAISS_INDEX_FILE_PATH}...")
            # Use faiss.read_index for the manually saved binary file
            faiss_index_obj = faiss.read_index(str(FAISS_INDEX_FILE_PATH))
            logger.info(f"FAISS index loaded successfully with {faiss_index_obj.ntotal} vectors.")

            logger.info(f"Loading metadata map from {DOC_METADATA_FILE_PATH}...")
            # Load the JSON map we created {faiss_id_str: {doc_id, text, metadata}}
            with open(DOC_METADATA_FILE_PATH, 'r', encoding='utf-8') as f:
                doc_metadata = json.load(f)
            logger.info(f"Metadata map loaded successfully with {len(doc_metadata)} entries.")

            # Create LlamaIndex FaissVectorStore wrapper using the loaded index
            vector_store = FaissVectorStore(faiss_index=faiss_index_obj)

            # --- CRITICAL: Reconstruct nodes for LlamaIndex ---
            nodes = []
            logger.info("Reconstructing TextNode objects from metadata...")
            # Sort keys numerically to ensure order matches faiss_ids used during build
            sorted_faiss_ids = sorted(doc_metadata.keys(), key=int)

            for faiss_id_str in sorted_faiss_ids:
                meta_info = doc_metadata[faiss_id_str]
                if not isinstance(meta_info, dict): # Add check
                     logger.warning(f"Skipping invalid metadata entry for FAISS ID {faiss_id_str}")
                     continue
                # Recreate the TextNode object using data from our JSON map
                node = TextNode(
                     id_=meta_info.get("doc_id"), # Use meaningful doc_id as LlamaIndex node_id
                     text=meta_info.get("text", ""), # Get the full text
                     metadata=meta_info.get("metadata", {}) # Get the original metadata
                )
                nodes.append(node)
            logger.info(f"Reconstructed {len(nodes)} TextNode objects.")

            if not nodes:
                raise ValueError("No TextNode objects were reconstructed from metadata.")
            if len(nodes) != faiss_index_obj.ntotal:
                 logger.warning(f"Metadata node count ({len(nodes)}) does not match FAISS vector count ({faiss_index_obj.ntotal}).")

            # Create the VectorStoreIndex using the reconstructed nodes and the loaded vector store
            vector_index = VectorStoreIndex(
                 nodes=nodes,
                 vector_store=vector_store,
                 # embed_model=Settings.embed_model # Already set globally
            )
            logger.info("LlamaIndex VectorStoreIndex initialized successfully with manually loaded data.")

        except Exception as e:
            logger.error(f"Failed during manual FAISS load or VectorStoreIndex init: {e}", exc_info=True)
            vector_index = None # Ensure it's None on failure
    else:
        logger.error(f"FAISS index file ({FAISS_INDEX_FILE_PATH}) or metadata file ({DOC_METADATA_FILE_PATH}) not found.")
        vector_index = None
    # --- END OF FAISS LOADING ---

    # --- Connect to Neo4j (Graceful Failure Logic) ---
    logger.info("Attempting to connect to Neo4j...")
    try: # Top-level try block for Neo4j
        neo4j_uri = os.getenv("NEO4J_URI")
        neo4j_username = os.getenv("NEO4J_USERNAME")
        neo4j_password = os.getenv("NEO4J_PASSWORD")

        if neo4j_uri and neo4j_username and neo4j_password:
            logger.debug(f"Attempting Neo4j connection to {neo4j_uri}...")
            graph_store = Neo4jGraphStore( url=neo4j_uri, username=neo4j_username, password=neo4j_password, database="neo4j" )
            try: # Nested try for verification
                 graph_store.driver.verify_connectivity() # <<< This is where it tries to connect
                 logger.info("Neo4j connection verified.")
                 kg_index = KnowledgeGraphIndex(nodes=[], index_id="neo4j_kg", graph_store=graph_store) # <<< LINE 120 (approx)
                 logger.info("Neo4j Knowledge Graph Index initialized.")
            except Exception as conn_err:
                 logger.warning(f"Neo4j connection verification failed: {conn_err}. KG index will be disabled.")
                 # kg_index REMAINS None
        else:
            logger.warning("Neo4j credentials missing. KG index disabled.")
            # kg_index REMAINS None
    except ImportError:
         logger.error("neo4j package not installed.")
         kg_index = None # Ensure it's None
    except Exception as e:
        logger.error(f"Unexpected error during Neo4j setup: {e}", exc_info=True)
        kg_index = None # Ensure it's None
    # --- END OF NEO4J LOADING ---

    # --- Final Check & Return ---
    if vector_index is None and kg_index is None: logger.error("CRITICAL: Both Vector Index and KG Index failed to load.")
    elif vector_index is None: logger.warning("RAG Engines Load Status: Vector Index FAILED. KG Index Status: " + ("Loaded" if kg_index else "FAILED/Disabled"))
    elif kg_index is None: logger.warning("RAG Engines Load Status: Vector Index Loaded. KG Index Status: FAILED/Disabled.")
    else: logger.info("RAG Engines Load Status: Both Vector and KG Indexes appear loaded.")

    return vector_index, kg_index


def query_rag(vector_index: Optional[VectorStoreIndex], kg_index: Optional[KnowledgeGraphIndex], question: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    Query the RAG system with a question using a Router.
    Handles cases where one or both indexes might be None.
    Returns tuple of (answer, sources_info)
    """
    if not vector_index and not kg_index:
        logger.error("Query attempted but no RAG indexes are loaded.")
        return "Error: The RAG system components are not available.", []

    try:
        query_engine_tools = []

        if vector_index: # Handles None case
            vector_tool = QueryEngineTool.from_defaults(
                query_engine=vector_index.as_query_engine(similarity_top_k=5),
                name="VectorLookupTool",
                description="Use for simple lookups, definitions, FAQs, symptoms, causes, treatments, or overviews."
            )
            query_engine_tools.append(vector_tool); logger.info("Vector Tool created.")

        if kg_index: # Handles None case
            kg_tool = QueryEngineTool.from_defaults(
                query_engine=kg_index.as_query_engine(include_text=False, response_mode="tree_summarize"),
                name="KnowledgeGraphTool",
                description="Use ONLY for complex questions about relationships."
            )
            query_engine_tools.append(kg_tool); logger.info("KG Tool created.")

        if not query_engine_tools:
            return "Error: No query tools created (Indexes failed?).", []

        if len(query_engine_tools) == 1:
            logger.info(f"Using single tool engine: {query_engine_tools[0].metadata.name}")
            query_engine = query_engine_tools[0].query_engine
        else:
            logger.info("Creating RouterQueryEngine...");
            query_engine = RouterQueryEngine.from_defaults(
                query_engine_tools=query_engine_tools,
                select_multi=False
            )
            logger.info("RouterQueryEngine created.")

        logger.info(f"Querying RAG system for: '{question}'")
        response = query_engine.query(question)
        logger.info("RAG system query complete.")

        answer = str(response) if response else "Could not retrieve answer."
        sources_info = []; processed_urls = set()

        if response and response.source_nodes:
            logger.info(f"Processing {len(response.source_nodes)} source nodes...")
            for scored_node in response.source_nodes:
                node = scored_node.node; metadata = node.metadata or {}
                src_name = metadata.get('name', f"Source ID: {node.node_id}")
                src_url = metadata.get('url', '')
                logger.debug(f"Source Node Metadata: {metadata}")
                if src_url and src_url not in processed_urls:
                    sources_info.append({"name": src_name, "url": src_url}); processed_urls.add(src_url)
                elif not src_url and src_name:
                    logger.debug(f"Source node missing URL: {src_name}")
                    # Optionally add sources without URLs
                    # if src_name not in [s['name'] for s in sources_info]:
                    #    sources_info.append({"name": src_name, "url": ""})

        logger.info(f"Extracted sources: {sources_info}")
        return answer, sources_info

    except Exception as e:
        logger.error(f"Error querying RAG system: {e}", exc_info=True)
        return f"Sorry, an error occurred.", []


# --- Placeholder functions (for chat_service.py) ---
# These are the functions routes_chat.py will import
def handle_chat_message(user_id, message, history, session_id):
    logger.warning("Placeholder handle_chat_message called. Implement real logic.")
    # In Phase 3, this will call Gemini Router, save to Firestore, etc.
    
    # --- For Phase 1/2 testing, let's make it call query_rag ---
    # This allows testing the RAG path via the chat endpoint
    
    # We need to get the indexes, which are loaded in _init_.py and stored in current_app
    from flask import current_app
    vector_index = current_app.config.get('VECTOR_INDEX')
    kg_index = current_app.config.get('KG_INDEX')
    
    # Simple Router: If question is short or a greeting, give canned response
    # Otherwise, assume it's a RAG query for now.
    if len(message.split()) < 3 or any(w in message.lower() for w in ['hi', 'hello', 'hey']):
        answer = "Hello! You can ask me a question about a medical condition, test, or drug."
        sources = []
        chat_type = "SYMPTOM" # Or 'GREETING'
    else:
        # Call our existing query_rag function
        answer, sources = query_rag(vector_index, kg_index, message)
        chat_type = "RAG"

    if not session_id:
        session_id = "session_" + os.urandom(8).hex()

    return answer, sources, chat_type, session_id


def generate_report(user_id, session_id):
    logger.warning(f"Placeholder generate_report called for session {session_id}.")
    # In Phase 3, this loads history from Firestore and calls Gemini chain
    summary = f"This is a placeholder summary for session {session_id}."
    triage = "Placeholder triage: We recommend consulting a General Practitioner (GP)."
    prep = "Placeholder prep kit:\n- What are my treatment options?\n- What are the side effects?"
    
    return summary, triage, prep