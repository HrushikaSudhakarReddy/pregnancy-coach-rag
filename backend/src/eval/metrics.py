from __future__ import annotations
from typing import List, Dict, Any, Optional
import time
import math
import re

def now_ms() -> float:
    return time.perf_counter() * 1000.0

def normalize_text(t: str) -> str:
    t = t.lower()
    t = re.sub(r"\s+", " ", t).strip()
    return t

def recall_at_k(relevants: List[int], k: int) -> float:
    return 1.0 if any(r < k for r in relevants) else 0.0

def mrr(relevants: List[int]) -> float:
    if not relevants:
        return 0.0
    rank = min(relevants) + 1  # 1-based
    return 1.0 / rank

def first_relevant_ranks(docs, gold_doc_ids: Optional[List[str]], gold_substrings: Optional[List[str]]) -> List[int]:
    ranks = []
    for idx, d in enumerate(docs):
        # Try several ways to get an id/text
        doc_id = d.get("id") or d.get("doc_id") or d.get("source") or (d.get("metadata",{}) or {}).get("id")
        text   = d.get("text") or d.get("page_content") or d.get("content") or ""

        if gold_doc_ids and doc_id and any(gid == str(doc_id) for gid in gold_doc_ids):
            ranks.append(idx)
            continue
        if gold_substrings:
            ntext = normalize_text(text)
            if any(normalize_text(s) in ntext for s in gold_substrings):
                ranks.append(idx)
                continue
    return ranks

def hallucination_heuristic(answer: str, citations: List[Dict[str,Any]] | List[str] | None, gold_substrings: Optional[List[str]]) -> int:
    """
    1 = hallucinated (likely), 0 = grounded (likely).
    Heuristics:
      - If no citations provided -> 1 (risky).
      - If gold_substrings are provided and *none* appear in answer -> 1.
      - Otherwise 0.
    Adjust to your system’s citation structure if needed.
    """
    if not citations:
        return 1
    if gold_substrings:
        nans = normalize_text(answer)
        if not any(normalize_text(s) in nans for s in gold_substrings):
            return 1
    return 0
