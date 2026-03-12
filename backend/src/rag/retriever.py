
from typing import List, Dict, Any, Callable
from ollama import Client
from config import OLLAMA_HOST, OLLAMA_EMBED_MODEL
from .chroma_store import get_collection

def _embed(text: str):
    client = Client(host=OLLAMA_HOST)
    res = client.embeddings(model=OLLAMA_EMBED_MODEL, prompt=text)
    return res.get("embedding", [])

def get_retriever() -> Callable:
    col = get_collection("pregnancy_kb")
    def _retriever(query: str, intent: str, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        q_emb = _embed(query)
        res = col.query(query_embeddings=[q_emb], n_results=4, include=["metadatas", "distances", "documents"])
        out: List[Dict[str, Any]] = []
        if res.get("ids"):
            for i in range(len(res["ids"][0])):
                md = res["metadatas"][0][i] if res.get("metadatas") else {}
                doc = res["documents"][0][i] if res.get("documents") else ""
                dist = float(res["distances"][0][i]) if res.get("distances") else 1.0
                out.append({
                    "source": md.get("source", ""),
                    "snippet": doc[:300].replace("\n"," "),
                    "score": 1.0 - dist
                })
        if not out:
            out.append({"source":"kb","snippet":"No retrieval results; using general guidance.","score":0.0})
        return out
    return _retriever
