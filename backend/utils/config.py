import os
import tempfile

from dotenv import load_dotenv

load_dotenv(".env")


def get_temp_dir() -> str:
    """Get temp directory path to store the files uploaded and makes sure it exists."""
    
    temp_dir = os.path.join(tempfile.gettempdir(), "HAYSTACK-RAG-TEMP-FILES")

    os.makedirs(temp_dir, exist_ok=True)

    return temp_dir


# MODEL_ID="google.gemma-3-12b-it"
MODEL_ID = os.getenv("MODEL_ID", "")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "")
# EMBEDDING_MODEL="amazon.titan-embed-text-v2:0"
HYBRID_EMBEDDING_MODEL = os.getenv("HYBRID_EMBEDDING_MODEL", "")
RAG_TEMPLATE_PATH = os.getenv("RAG_TEMPLATE_PATH", "")
SERPERDEV_API_KEY = os.getenv("SERPERDEV_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OPENSEARCH_INITIAL_ADMIN_PASSWORD = os.getenv("OPENSEARCH_INITIAL_ADMIN_PASSWORD", "")
OPENSEARCH_USERNAME = os.getenv("OPENSEARCH_USERNAME", "")
OPENSEARCH_PASSWORD = os.getenv("OPENSEARCH_PASSWORD", "")
TEMP_DIR: str = get_temp_dir()

