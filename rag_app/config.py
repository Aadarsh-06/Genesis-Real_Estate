import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_URI = os.getenv("POSTGRES_URI")
MONGO_URI = os.getenv("MONGO_URI")
# Fallback to key if env load fails
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDA1GYOD9ro_I3spP8MrYQcA6elXKD-q4E")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Models
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-004")
# Switch to Gemini 2.5 Flash model
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")

assert POSTGRES_URI, "POSTGRES_URI not set"
assert MONGO_URI, "MONGO_URI not set"
assert GEMINI_API_KEY, "GEMINI_API_KEY not set"