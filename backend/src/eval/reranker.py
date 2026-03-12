from __future__ import annotations
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer

class SimpleEmbeddingReranker:
    """
    Second-stage re-ranker: reorders retrieved docs by cosine similarity to the query.
    Uses the same small ST model so it's light.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def _embed(self, texts: List[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)

    def rerank(self, query: str, docs: List[Dict[str, Any]], text_key: str = "text") -> List[Dict[str, Any]]:
        if not docs:
            return docs
        q = self._embed([query])[0]
        D = self._embed([d.get(text_key) or d.get("page_content","") for d in docs])
        sims = (D @ q)  # cosine since vectors are normalized
        order = np.argsort(-sims)
        return [docs[i] for i in order]
