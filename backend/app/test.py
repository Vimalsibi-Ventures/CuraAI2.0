import os
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

import google.generativeai as genai

# Test your API key
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ ERROR: GOOGLE_API_KEY not found in environment variables")
    print("Available environment variables:")
    for key, value in os.environ.items():
        if 'GOOGLE' in key or 'API' in key:
            print(f"  {key}: {value}")
else:
    print(f"✅ API Key found: {api_key[:10]}...")  # Show first 10 chars for verification

    try:
        genai.configure(api_key=api_key)
        
        # List available models
        print("\n📋 Available models:")
        models = genai.list_models()
        for model in models:
            if 'gemini' in model.name.lower():
                print(f"  - {model.name}")
        
        # Simple test
        print("\n🧪 Testing model...")
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content("Hello, how are you? Respond in one sentence.")
        print("✅ Response:", response.text)
        
    except Exception as e:
        print(f"❌ Error: {e}")