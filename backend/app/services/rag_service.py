import os
from llama_index import (
    Settings,
    HuggingFaceEmbedding,
    load_index_from_storage,
    StorageContext,
    KnowledgeGraphIndex,
    Neo4jGraphStore,
    RouterQueryEngine,
    QueryEngineTool
)

def load_rag_engines():
    vector_index = None
    kg_index = None

    # Load embedding model
    embed_model = HuggingFaceEmbedding('sentence-transformers/all-MiniLM-L6-v2')
    Settings.embed_model = embed_model

    # Load FAISS index
    try:
        vector_index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir="../storage/faiss_llamaindex_storage")
        )
    except FileNotFoundError:
        print("FAISS index not found at ../storage/faiss_llamaindex_storage")

    # Connect to Neo4j and create KG index
    try:
        neo4j_url = os.getenv("NEO4J_URL")
        neo4j_user = os.getenv("NEO4J_USER")
        neo4j_password = os.getenv("NEO4J_PASSWORD")

        graph_store = Neo4jGraphStore(
            host=neo4j_url,
            username=neo4j_user,
            password=neo4j_password
        )
        kg_index = KnowledgeGraphIndex(graph_store=graph_store)
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")

    return vector_index, kg_index


def query_rag(vector_index, kg_index, question):
    if not vector_index and not kg_index:
        return "Error: RAG indexes not loaded", []

    tools = []

    if vector_index:
        vector_tool = QueryEngineTool(
            query_engine=vector_index.as_query_engine(),
            name="VectorLookup",
            description="Use this tool to look up FAQs and document content"
        )
        tools.append(vector_tool)

    if kg_index:
        kg_tool = QueryEngineTool(
            query_engine=kg_index.as_query_engine(),
            name="KnowledgeGraphLookup",
            description="Use this tool to explore entity relationships in Neo4j"
        )
        tools.append(kg_tool)

    query_engine = RouterQueryEngine(tools=tools)
    response = query_engine.query(question)

    answer = str(response)

    sources_info = []
    if hasattr(response, "source_nodes"):
        for node in response.source_nodes:
            metadata = getattr(node, "metadata", {})
            name = metadata.get("name")
            url = metadata.get("url")
            if name or url:
                sources_info.append({"name": name, "url": url})

    # Remove duplicates
    unique_sources = [dict(t) for t in {tuple(d.items()) for d in sources_info}]

    return answer, unique_sources
