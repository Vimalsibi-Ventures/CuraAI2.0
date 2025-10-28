import logging
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from app.models import RAGRequest, RAGResponse
from app.services.rag_service import query_rag

logger = logging.getLogger(__name__)

rag_bp = Blueprint('rag', __name__, url_prefix='/api/rag')


@rag_bp.route('/rag_query', methods=['POST'])
# TODO: Add @token_required decorator in Phase 3
def rag_query_route():
    logger.info("RAG query route hit.")
    vector_index = current_app.config.get("VECTOR_INDEX")
    kg_index = current_app.config.get("KG_INDEX")

    if not vector_index and not kg_index:
        logger.error("RAG query failed: Indexes not loaded.")
        return jsonify({"error": "RAG indexes not loaded"}), 500

    try:
        req_data = RAGRequest(**request.json)
    except ValidationError as e:
        logger.error(f"RAG request validation error: {e.json()}")
        return jsonify({"error": "Invalid request data", "details": e.errors()}), 400
    except Exception as e:
        logger.error(f"Invalid JSON data: {e}")
        return jsonify({"error": f"Invalid JSON data: {e}"}), 400

    try:
        answer, sources = query_rag(vector_index, kg_index, req_data.user_question)
        response_data = RAGResponse(answer=answer, sources=sources)
        return jsonify(response_data.model_dump()) # Use .model_dump()
    except Exception as e:
        logger.error(f"Error during RAG query in route: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500