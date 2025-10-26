from flask import Blueprint, request, jsonify, current_app
from app.models import RAGRequest, RAGResponse
from app.services.rag_service import query_rag

rag_bp = Blueprint('rag', __name__, url_prefix='/api/rag')


@rag_bp.route('/rag_query', methods=['POST'])
def rag_query():
    vector_index = current_app.config.get("VECTOR_INDEX")
    kg_index = current_app.config.get("KG_INDEX")

    if not vector_index and not kg_index:
        return jsonify({"error": "RAG indexes not loaded"}), 500

    try:
        req_data = RAGRequest(**request.json)
    except Exception as e:
        return jsonify({"error": f"Invalid request data: {e}"}), 400

    answer, sources = query_rag(vector_index, kg_index, req_data.user_question)

    return jsonify(RAGResponse(answer=answer, sources=sources).dict())
