import os
from dotenv import load_dotenv

load_dotenv()

# Load from .env file only
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Models
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-004")

# Switch to Gemini 2.5 Flash model (default)
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")

assert GEMINI_API_KEY, "GEMINI_API_KEY not set"