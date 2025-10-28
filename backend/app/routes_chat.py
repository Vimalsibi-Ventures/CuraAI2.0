import logging
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from functools import wraps

# Import the API Contract models defined in models.py
from app.models import ChatRequest, ChatResponse, ReportRequest, ReportResponse

# Import the service functions at the top level
from app.services.chat_service import handle_chat_message, generate_report

logger = logging.getLogger(__name__)

# Define the Blueprint
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# --- JWT Authentication Decorator (Placeholder) ---
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = "placeholder_user_id" # Placeholder
        # TODO: Add real JWT validation logic here in Phase 3
        if current_app.debug:
            logger.warning("Auth token check skipped in debug mode.")
            user_id = "debug_user"
        # else:
            # Add real token checking here
            # pass 
        return f(user_id, *args, **kwargs)
    return decorated_function
# --- End Auth Decorator ---


@chat_bp.route('/message', methods=['POST'])
@token_required
def handle_message_route(user_id):
    """Handles incoming chat messages, routes them, saves history."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        chat_request = ChatRequest(**data)
        logger.info(f"Received chat message from user: {user_id}, session: {chat_request.session_id}")

        answer, sources, chat_type, session_id = handle_chat_message(
            user_id=user_id,
            message=chat_request.message,
            history=chat_request.history,
            session_id=chat_request.session_id
        )

        response_data = ChatResponse(
            answer=answer,
            sources=sources,
            type=chat_type,
            session_id=session_id
        )
        return jsonify(response_data.model_dump())

    except ValidationError as e:
        logger.error(f"Chat message validation error: {e.json()}")
        return jsonify({'error': 'Invalid request data', 'details': e.errors()}), 400
    except Exception as e:
        logger.error(f"Error handling chat message: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@chat_bp.route('/report', methods=['POST'])
@token_required
def generate_report_route(user_id):
    """Generates the final report based on a chat session."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        report_request = ReportRequest(**data)
        logger.info(f"Received report request from user: {user_id}, session: {report_request.session_id}")

        summary, triage, prep = generate_report(
            user_id=user_id,
            session_id=report_request.session_id
        )

        response_data = ReportResponse(
            summary=summary,
            triage=triage,
            prep=prep
        )
        return jsonify(response_data.model_dump())

    except ValidationError as e:
        logger.error(f"Report request validation error: {e.json()}")
        return jsonify({'error': 'Invalid request data', 'details': e.errors()}), 400
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500