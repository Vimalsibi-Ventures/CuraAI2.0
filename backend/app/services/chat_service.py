import logging
import os
import json
import re 
from flask import current_app
from typing import List, Dict, Tuple, Any

from app.services.rag_service import query_rag
from llama_index.core import Settings 

try:
    from app.models import ChatMessage
except ImportError:
    class ChatMessage:
        role: str
        content: str

logger = logging.getLogger(__name__)

def _parse_json_list(llm_output: str) -> List[str]:
    try:
        match = re.search(r'\[.*?\]', llm_output, re.DOTALL)
        if match:
            json_str = match.group(0)
            data = json.loads(json_str)
            if isinstance(data, list):
                return [str(item) for item in data]
        
        logger.warning(f"Could not find valid JSON list in LLM output: {llm_output}")
        return []
    except Exception as e:
        logger.error(f"Failed to parse JSON from LLM output: {e}. Output was: {llm_output}")
        return []

def handle_chat_message(message: str, history: List[ChatMessage], session_id: str) -> Tuple[str, List[Dict[str, Any]], str, str]:
    logger.info(f"Handling smart chat message for session {session_id}...")
    llm = Settings.llm
    if not llm:
        logger.error("LLM (Settings.llm) is not available.")
        return "Sorry, the AI service is not configured.", [], "SYMPTOM", session_id

    history_str = "\n".join([f"{msg.role}: {msg.content}" for msg in history])
    
    router_prompt = f"""You are a routing agent. The user's latest message is: {message}
The full chat history is:
{history_str}
Is the user asking a factual Q&A (e.g., 'What is an MRI?'), or are they describing their symptoms?
Respond only with the word RAG or SYMPTOM."""
    
    try:
        response = llm.complete(router_prompt)
        chat_mode = str(response).strip().upper()
    except Exception as e:
        # --- NEW EXCEPTION HANDLING ---
        logger.error(f"Router LLM call failed. This is likely an API key or quota issue: {e}", exc_info=True)
        # We can't route, so we'll just apologize.
        return "Sorry, I'm having trouble connecting to the AI service. Please check the backend API key.", [], "SYMPTOM", session_id

    if "RAG" in chat_mode:
        chat_mode = "RAG"
        logger.info(f"Router selected: {chat_mode}")
        vector_index = current_app.config.get('VECTOR_INDEX')
        kg_index = current_app.config.get('KG_INDEX')

        if not vector_index and not kg_index:
             logger.error("Chat Router: RAG engines not loaded in app config.")
             answer = "Sorry, the RAG system is not available right now."
             sources = []
        else:
            logger.info(f"Routing message to RAG service...")
            # This function (query_rag) already has its own try/except
            answer, sources = query_rag(vector_index, kg_index, message)
            logger.info("RAG service returned answer.")

    else:
        chat_mode = "SYMPTOM"
        logger.info(f"Router selected: {chat_mode}")
        
        nurse_prompt = f"""You are an empathetic nurse. The chat history is:
{history_str}
The user just said: {message}
Ask one simple, clarifying question to better understand their symptoms (e.g., 'Where does it hurt?', 'How long have you felt this way?').
If the history is vague, ask a clarifying question. Do not sound like a robot."""
        
        try:
            nurse_response = llm.complete(nurse_prompt)
            answer = str(nurse_response).strip()
            sources = []
        except Exception as e:
            # --- NEW EXCEPTION HANDLING ---
            logger.error(f"Nurse LLM call failed. This is likely an API key or quota issue: {e}", exc_info=True)
            answer = "Sorry, I'm having trouble connecting to the AI service. Please check the backend API key."
            sources = []

    if not session_id:
        session_id = "session_" + os.urandom(8).hex()

    return answer, sources, chat_mode, session_id

def generate_report(history: List[ChatMessage]) -> Tuple[List[str], List[str]]:
    logger.info(f"Generating smart report from history ({len(history)} messages)...")
    llm = Settings.llm
    if not llm:
        logger.error("LLM (Settings.llm) is not available for report generation.")
        return ["Error: AI service not configured"], ["Error: AI service not configured"]

    history_str = "\n".join([f"{msg.role}: {msg.content}" for msg in history if msg.role == 'user' or 'symptom' in msg.content.lower()])

    if not history_str:
        logger.warning("Report generated with no usable history.")
        return ["No symptom data provided."], ["No questions generated."]

    disease_list = []
    question_list = []

    try:
        doctor_prompt = f"""You are a medical analyst. Analyze this chat history:
{history_str}
Based only on the symptoms, what are the top 3-5 possible diseases or conditions?
Respond with only a JSON list of strings, like ["Migraine", "Tension Headache"]."""
        
        disease_response = llm.complete(doctor_prompt)
        disease_list = _parse_json_list(str(disease_response))
        logger.info(f"Doctor Report call successful, found {len(disease_list)} diseases.")
        
    except Exception as e:
        # --- NEW EXCEPTION HANDLING ---
        logger.error(f"Doctor Report LLM call failed: {e}", exc_info=True)
        disease_list = ["Error processing medical analysis. Check API key."]

    try:
        patient_prompt = f"""You are a helpful patient advocate. Based on this chat history:
{history_str}
Generate a JSON list of 5 concise questions the patient should ask their doctor, like ["What are the possible side effects?", "Are there alternative treatments?"]."""
        
        question_response = llm.complete(patient_prompt)
        question_list = _parse_json_list(str(question_response))
        logger.info(f"Patient Report call successful, found {len(question_list)} questions.")

    except Exception as e:
        # --- NEW EXCEPTION HANDLING ---
        logger.error(f"Patient Report LLM call failed: {e}", exc_info=True)
        question_list = ["Error processing patient questions. Check API key."]

    if not disease_list:
        disease_list = ["No specific conditions identified."]
    if not question_list:
        question_list = ["No specific questions generated. Be sure to describe all symptoms to your doctor."]

    return disease_list, question_list
