from flask import Blueprint, request, jsonify
from app.models import ChatMessageRequest, ChatMessageResponse, ReportRequest, ReportResponse
from app.services.chat_service import handle_chat_message, generate_report

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')


@chat_bp.route('/message', methods=['POST'])
def chat_message():
    try:
        req_data = ChatMessageRequest(**request.json)
    except Exception as e:
        return jsonify({"error": f"Invalid request: {e}"}), 400

    response = handle_chat_message(
        req_data.user_id, req_data.message, req_data.history, req_data.session_id
    )
    return jsonify(ChatMessageResponse(**response).dict())


@chat_bp.route('/report', methods=['POST'])
def chat_report():
    try:
        req_data = ReportRequest(**request.json)
    except Exception as e:
        return jsonify({"error": f"Invalid request: {e}"}), 400

    response = generate_report(req_data.user_id, req_data.session_id)
    return jsonify(ReportResponse(**response).dict())
