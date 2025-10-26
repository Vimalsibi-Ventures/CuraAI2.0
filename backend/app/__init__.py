import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

def create_app():
    """Application factory for the Flask backend."""

    # Load environment variables from project root (.env)
    env_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, '.env')
    )
    load_dotenv(env_path)

    # Initialize Flask app
    app = Flask(__name__)

    # Set secret key for sessions
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default_secret_key_change_me')

    # Enable CORS for all /api/* routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # -----------------------------
    # Load RAG engines (FAISS + KG)
    # -----------------------------
    try:
        from app.services.rag_service import load_rag_engines
        vector_index, kg_index = load_rag_engines()
        app.config['VECTOR_INDEX'] = vector_index
        app.config['KG_INDEX'] = kg_index
    except Exception as e:
        print(f"Warning: Failed to load RAG engines: {e}")
        app.config['VECTOR_INDEX'] = None
        app.config['KG_INDEX'] = None

    # -----------------------------
    # Import & register blueprints
    # -----------------------------
    from app.routes_auth import auth_bp
    app.register_blueprint(auth_bp)

    # Optional: RAG blueprint
    try:
        from app.routes_rag import rag_bp
        app.register_blueprint(rag_bp)
    except ImportError:
        print("RAG blueprint not loaded (routes_rag.py missing).")

    # Optional: Chat blueprint
    try:
        from app.routes_chat import chat_bp
        app.register_blueprint(chat_bp)
    except ImportError:
        print("Chat blueprint not loaded (routes_chat.py missing).")

    return app
