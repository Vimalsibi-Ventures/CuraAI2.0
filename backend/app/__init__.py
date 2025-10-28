import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def create_app():
    """Application factory for the Flask backend."""
    logger.info("Creating Flask app instance...")

    # Load environment variables from project root (.env)
    # This path assumes __init__.py is in 'app' and .env is two levels up
    env_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, '.env')
    )
    if os.path.exists(env_path):
        load_dotenv(env_path)
        logger.info(f"Loaded environment variables from: {env_path}")
    else:
        logger.warning(f".env file not found at {env_path}, relying on system vars.")

    # Initialize Flask app
    app = Flask(__name__)

    # Set secret key for sessions
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default_secret_key_change_me')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret_key_change_me')

    # Enable CORS
    # CORS(app, resources={r"/api/*": {"origins": "*"}}) # 👈 This was too specific and failed the preflight
    CORS(app) # 👈 NEW: Apply a default, wide-open CORS policy to the entire app.
    logger.info("Applied wide-open CORS policy to the app.")

    # -----------------------------
    # Load RAG engines (FAISS + KG)
    # -----------------------------
    app.config['VECTOR_INDEX'] = None # Initialize as None
    app.config['KG_INDEX'] = None    # Initialize as None
    try:
        from app.services.rag_service import load_rag_engines
        logger.info("Imported load_rag_engines. Attempting to load...")
        vector_index_loaded, kg_index_loaded = load_rag_engines()
        app.config['VECTOR_INDEX'] = vector_index_loaded
        app.config['KG_INDEX'] = kg_index_loaded
        
        if vector_index_loaded and kg_index_loaded:
            logger.info("RAG Engines (Vector Index + KG Index) loaded successfully.")
        elif vector_index_loaded:
            logger.warning("RAG Engines: Vector Index loaded, KG Index FAILED.")
        elif kg_index_loaded:
             logger.warning("RAG Engines: KG Index loaded, Vector Index FAILED.")
        else:
             logger.error("CRITICAL: Both Vector Index and KG Index FAILED to load.")

    except ImportError as e:
        logger.error(f"ImportError: Failed to import 'load_rag_engines' from 'app.services.rag_service'. Check file and function names. Error: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Error during RAG engine loading in __init__: {e}", exc_info=True)

    # -----------------------------
    # Import & register blueprints
    # -----------------------------
    try:
        from app.routes_auth import auth_bp
        app.register_blueprint(auth_bp)
        logger.info("Auth blueprint registered.")
    except ImportError as e:
        logger.error(f"Auth blueprint FAILED to load (routes_auth.py missing or error): {e}", exc_info=True)
    except Exception as e:
         logger.error(f"Error registering auth blueprint: {e}", exc_info=True)

    try:
        from app.routes_rag import rag_bp
        app.register_blueprint(rag_bp)
        logger.info("RAG blueprint registered.")
    except ImportError as e:
        logger.error(f"RAG blueprint FAILED to load (routes_rag.py missing or error): {e}", exc_info=True)
    except Exception as e:
         logger.error(f"Error registering RAG blueprint: {e}", exc_info=True)

    try:
        from app.routes_chat import chat_bp
        app.register_blueprint(chat_bp)
        logger.info("Chat blueprint registered successfully.")
    except ImportError as e:
        logger.error(f"Chat blueprint FAILED to load (routes_chat.py missing or error): {e}", exc_info=True)
    except Exception as e:
         logger.error(f"Error registering chat blueprint: {e}", exc_info=True)

    # --- NEW: Register the Misc (Location) Blueprint ---
    try:
        from app.routes_misc import misc_bp
        app.register_blueprint(misc_bp)
        logger.info("Misc blueprint (for location) registered successfully.")
    except ImportError as e:
        logger.error(f"Misc blueprint FAILED to load (routes_misc.py missing or error): {e}", exc_info=True)
    except Exception as e:
         logger.error(f"Error registering misc blueprint: {e}", exc_info=True)
    # --- End New Code ---

    logger.info("Flask app instance creation complete.")
    return app

