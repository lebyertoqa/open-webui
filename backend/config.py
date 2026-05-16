import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

####################################
# Base Paths
####################################

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

####################################
# Database
####################################

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/webui.db")

####################################
# Security / Auth
####################################

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "changeme-please-set-a-strong-secret-key-in-production",
)

JWT_ALGORITHM = "HS256"
JWT_EXPIRES_IN = int(os.getenv("JWT_EXPIRES_IN", 60 * 60 * 24 * 7))  # 7 days in seconds

# Whether new user registrations are allowed
ENABLE_SIGNUP = os.getenv("ENABLE_SIGNUP", "true").lower() == "true"

# Default user role assigned on signup
DEFAULT_USER_ROLE = os.getenv("DEFAULT_USER_ROLE", "user")  # "user" | "admin" | "pending"

####################################
# CORS
####################################

CORS_ALLOW_ORIGIN = os.getenv("CORS_ALLOW_ORIGIN", "*")

####################################
# Ollama
####################################

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_API_BASE_URL = f"{OLLAMA_BASE_URL}/api"  # kept for backwards compat

####################################
# OpenAI
####################################

OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
OPENAI_API_BASE_URL = os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com/v1")

####################################
# RAG / Vector Store
####################################

CHROMA_DATA_PATH = str(DATA_DIR / "vector_db")
CHROMA_HTTP_HOST = os.getenv("CHROMA_HTTP_HOST", "")
CHROMA_HTTP_PORT = int(os.getenv("CHROMA_HTTP_PORT", 8000))

# Embedding model used for RAG
RAG_EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Top-k documents retrieved for context
RAG_TOP_K = int(os.getenv("RAG_TOP_K", 5))

####################################
# Uploads
####################################

UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", 50))
MAX_UPLOAD_SIZE = MAX_UPLOAD_SIZE_MB * 1024 * 1024  # bytes

####################################
# Logging
####################################

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

####################################
# App Metadata
####################################

APP_NAME = os.getenv("APP_NAME", "Open WebUI")
APP_VERSION = "0.1.0"
FRONTEND_BUILD_DIR = BASE_DIR.parent / "build"
