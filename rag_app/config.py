import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_URI = os.getenv("POSTGRES_URI")
MONGO_URI = os.getenv("MONGO_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI models
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")

assert POSTGRES_URI, "POSTGRES_URI not set"
assert MONGO_URI, "MONGO_URI not set"
assert OPENAI_API_KEY, "OPENAI_API_KEY not set"