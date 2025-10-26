import os
import logging
from llama_index.core import ( # CORRECTED Settings import
    Settings,
    load_index_from_storage,
    StorageContext,
    KnowledgeGraphIndex
)
from llama_index.core.query_engine import RouterQueryEngine # Correct import
from llama_index.core.tools import QueryEngineTool # Correct import
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.graph_stores.neo4j import Neo4jGraphStore

logger = logging.getLogger(__name__)

# Define storage path relative to this file's location
SCRIPT_DIR = os.path.dirname(__file__)
STORAGE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', 'storage')) # Go up two levels to backend/storage
FAISS_PERSIST_DIR = os.path.join(STORAGE_DIR, "faiss_llamaindex_storage")

def load_rag_engines():
    """Loads the FAISS vector index and initializes the Neo4j KG index."""
    vector_index = None
    kg_index = None
    logger.info("Attempting to load RAG engines...")

    # --- Load Local Embedding Model ---
    # Needs to be set before loading FAISS index if embeddings aren't stored with index
    try:
        embed_model = HuggingFaceEmbedding(model_name='sentence-transformers/all-MiniLM-L6-v2')
        Settings.embed_model = embed_model
        logger.info("Local embedding model loaded and set in Settings.")
    except Exception as e:
        logger.error(f"Failed to load local embedding model: {e}", exc_info=True)
        # Depending on requirements, might want to raise error or continue without embeddings

    # --- Load FAISS Vector Index ---
    logger.info(f"Attempting to load FAISS index from: {FAISS_PERSIST_DIR}")
    if os.path.exists(FAISS_PERSIST_DIR):
        try:
            if Settings.embed_model is None:
                raise RuntimeError("Cannot load FAISS: Embed model must be loaded first.")
            storage_context = StorageContext.from_defaults(persist_dir=FAISS_PERSIST_DIR)
            vector_index = load_index_from_storage(storage_context)
            logger.info("FAISS Vector index loaded successfully from storage.")
        except Exception as e:
            logger.error(f"Failed to load FAISS index from {FAISS_PERSIST_DIR}: {e}", exc_info=True)
    else:
        logger.warning(f"FAISS index storage directory not found: {FAISS_PERSIST_DIR}")

    # --- Connect to Neo4j and Create KG Index Wrapper ---
    logger.info("Attempting to connect to Neo4j...")
    try:
        neo4j_uri = os.getenv("NEO4J_URI") # Changed from NEO4J_URL for consistency
        neo4j_user = os.getenv("NEO4J_USERNAME") # Changed from NEO4J_USER
        neo4j_password = os.getenv("NEO4J_PASSWORD") # Changed from NEO4J_PASS

        if neo4j_uri and neo4j_user and neo4j_password:
            graph_store = Neo4jGraphStore(
                url=neo4j_uri, # CORRECTED parameter name
                username=neo4j_user,
                password=neo4j_password,
                database="neo4j" # Explicitly set default, change if needed
            )
            # Initialize wrapper - does not load nodes from disk here
            kg_index = KnowledgeGraphIndex(nodes=[], index_id="neo4j_kg", graph_store=graph_store)
            logger.info("Neo4j Knowledge Graph Index initialized.")
        else:
            logger.warning("Neo4j credentials (URI, USERNAME, PASSWORD) missing in environment. KG index disabled.")

    except ImportError:
         logger.error("`neo4j` package not installed. Cannot connect to Neo4j. Run `pip install neo4j`")
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j or initialize KG Index: {e}", exc_info=True)

    if vector_index is None and kg_index is None:
        logger.error("CRITICAL: Both Vector Index and KG Index failed to load.")
    elif vector_index is None:
         logger.warning("Warning: Vector Index failed to load.")
    elif kg_index is None:
         logger.warning("Warning: KG Index failed to load.")

    return vector_index, kg_index


def query_rag(vector_index, kg_index, question):
    """Queries the appropriate RAG engine based on available indexes."""
    if not vector_index and not kg_index:
        logger.error("Query attempted but no RAG indexes are loaded.")
        return "Error: RAG system is not available.", []

    tools = []

    # Create tools using the CORRECTED 'from_defaults' method
    if vector_index:
        vector_tool = QueryEngineTool.from_defaults(
            query_engine=vector_index.as_query_engine(similarity_top_k=5),
            name="VectorLookupTool", # Names should be unique and descriptive
            description="Use for simple lookups, definitions, FAQs, or overviews for a specific disease, test, or drug."
        )
        tools.append(vector_tool)
        logger.info("Vector Tool created.")

    if kg_index:
        kg_tool = QueryEngineTool.from_defaults(
            query_engine=kg_index.as_query_engine(include_text=False, response_mode="tree_summarize"),
            name="KnowledgeGraphTool", # Unique name
            description="Use ONLY for complex questions about *relationships* between diseases, symptoms, tests, and drugs."
        )
        tools.append(kg_tool)
        logger.info("KG Tool created.")

    if not tools:
        # Should not happen if initial check passed, but good safeguard
        return "Error: No query tools could be created.", []

    # Create Router using CORRECTED 'query_engine_tools' argument
    query_engine = RouterQueryEngine.from_defaults(
        query_engine_tools=tools,
        select_multi=False # Router selects the single best tool
        )
    logger.info("RouterQueryEngine created.")

    try:
        logger.info(f"Querying Router Engine for: '{question}'")
        response = query_engine.query(question)
        logger.info("Router Engine query complete.")
    except Exception as e:
        logger.error(f"Error during Router Engine query: {e}", exc_info=True)
        return "Sorry, I encountered an error trying to find an answer.", []

    answer = str(response) if response else "I couldn't retrieve an answer based on the available information."

    # Extract sources correctly from metadata
    sources_info = []
    processed_urls = set() # Use a set for efficient duplicate checking
    if response and response.source_nodes:
        logger.info(f"Processing {len(response.source_nodes)} source nodes...")
        for scored_node in response.source_nodes:
            node = scored_node.node
            metadata = node.metadata or {}
            # Use 'name' from metadata, fall back to a default if missing
            src_name = metadata.get('name', f"Source ID: {node.node_id}")
            src_url = metadata.get('url', '')

            logger.debug(f"Source Node Metadata: {metadata}")

            # Add source if URL is present and not already added
            if src_url and src_url not in processed_urls:
                sources_info.append({"name": src_name, "url": src_url})
                processed_urls.add(src_url)
            elif not src_url:
                # Still add source if no URL but has a name, if desired
                # Or log a warning if URL is expected
                logger.debug(f"Source node missing URL: {src_name}")
                # Optionally add sources without URLs if needed:
                # sources_info.append({"name": src_name, "url": ""})

    logger.info(f"Extracted sources: {sources_info}")
    return answer, sources_info

# --- Placeholder functions for chat service ---
# These will be implemented in Phase 3
def handle_chat_message(user_id, message, history, session_id):
    logger.warning("handle_chat_message is a placeholder.")
    # Dummy implementation for Phase 1/2
    answer = "Chat message received (placeholder response)."
    sources = []
    chat_mode = "SYMPTOM" # Assume symptom for now
    new_session_id = session_id or "dummy_session_" + str(os.urandom(4).hex())
    # TODO: Implement actual logic using Gemini Router, RAG, Nurse prompt, Firestore
    return answer, sources, chat_mode, new_session_id

def generate_report(user_id, session_id):
    logger.warning("generate_report is a placeholder.")
    # Dummy implementation for Phase 1/2
    summary = "This is a placeholder summary based on session " + session_id
    triage = "Placeholder triage: See GP."
    prep = "Placeholder prep kit: Ask about X, Y, Z."
    # TODO: Implement actual logic using Firestore load, Gemini chain
    return summary, triage, prep