import logging
import os
import json
from flask import current_app # Import current_app to access RAG engines

# Import the RAG function we need
from app.services.rag_service import query_rag

# Import Gemini LLM settings (assuming it's set globally)
from llama_index.core import Settings 
# from llama_index.llms.google_genai import GoogleGenerativeAI # Not needed if using Settings.llm

logger = logging.getLogger(__name__)

# This is a STUB/PLACEHOLDER implementation for Phase 1/2
# B3 / Chat team will replace this in Phase 3
def handle_chat_message(user_id, message, history, session_id):
    logger.info(f"Handling chat message for user {user_id}...")
    
    # --- Placeholder Router Logic ---
    # In a real app, this calls Gemini. For now, assume it's RAG.
    chat_mode = "RAG" # Default to RAG for this stub
    
    if chat_mode == "RAG":
        # Get the loaded RAG engines from the Flask app config
        vector_index = current_app.config.get('VECTOR_INDEX')
        kg_index = current_app.config.get('KG_INDEX')

        if not vector_index and not kg_index:
             logger.error("Chat Router: RAG engines not loaded in app config.")
             answer = "Sorry, the RAG system is not available right now."
             sources = []
        else:
            # Call our existing query_rag function
            logger.info(f"Routing message to RAG service...")
            answer, sources = query_rag(vector_index, kg_index, message)
            logger.info("RAG service returned answer.")
    
    else:
        # Placeholder Nurse bot logic
        logger.info("Routing message to placeholder Nurse bot...")
        answer = "Placeholder Nurse bot: Tell me more about that."
        sources = []

    if not session_id:
        session_id = "session_" + os.urandom(8).hex()

    return answer, sources, chat_mode, session_id

def generate_report(user_id, session_id):
    logger.info(f"Placeholder: Generating report for user {user_id}, session {session_id}")
    # In Phase 3, this loads history from Firestore and calls Gemini chain
    summary = f"This is a placeholder summary for session {session_id}."
    triage = "Placeholder triage: We recommend consulting a General Practitioner (GP)."
    prep = "Placeholder prep kit:\n- What are my treatment options?\n- What are the side effects?"
    
    return summary, triage, prep