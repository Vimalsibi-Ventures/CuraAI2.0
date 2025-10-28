import os
import sys
import logging

# --- Add project root to Python path ---
# This ensures imports like 'from app import create_app' work when running from the root directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # Path to this main.py file (app/)
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir)) # Path to backend/
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
# --- End Path Setup ---

# --- Load .env file from project root ---
# Needs to happen before create_app() is called if create_app uses os.getenv
try:
    from dotenv import load_dotenv
    # Go up one level from backend/ to find the root .env
    dotenv_path = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir, '.env'))
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
        print(f"Loaded environment variables from: {dotenv_path}") # Optional confirmation
    else:
        print(f".env file not found at {dotenv_path}. Relying on system environment variables.")
except ImportError:
    print("python-dotenv not installed, cannot load .env file.")
except Exception as e:
    print(f"Error loading .env file: {e}")
# --- End .env loading ---


# --- Import the App Factory ---
# Imports from the 'app' package (defined by the _init_.py file)
try:
    from app import create_app
except ImportError as e:
    print(f"Error: Could not import create_app from app package: {e}")
    print("Ensure _init_.py exists in the 'app' folder and doesn't have import errors itself.")
    sys.exit(1) # Exit if the core app cannot be imported

# --- Global Logger Setup (Optional but good practice) ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)


# --- Create and Run the App ---
logger.info("Creating Flask app instance...")
app = create_app()
logger.info("Flask app instance created.")

if __name__ == '__main__':
    # Use Gunicorn for production, but Flask dev server is fine for local testing/hackathon
    port = int(os.environ.get('PORT', 5050)) # Changed default port to 5000 (common for Flask)
    logger.info(f"Starting Flask development server on http://0.0.0.0:{port}")
    # debug=True enables auto-reloading and better error pages during development
    # Use debug=False for more production-like testing
    app.run(host='0.0.0.0', port=port, debug=True)