
import chromadb
from chromadb.config import Settings
from typing import Optional
from config import CHROMA_PERSIST_DIR

_client: Optional[chromadb.Client] = None

def get_client() -> chromadb.Client:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR, settings=Settings(allow_reset=True))
    return _client

def get_collection(name: str = "pregnancy_kb"):
    client = get_client()
    return client.get_or_create_collection(name=name)  # using manual embeddings
