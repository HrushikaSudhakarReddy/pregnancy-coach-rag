from __future__ import annotations
import argparse, json, jsonlines
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import matplotlib.pyplot as plt
import time

from src.rag.retriever import get_retriever
from src.chains.answer import compose_answer
from src.eval.metrics import now_ms, first_relevant_ranks, recall_at_k, mrr, hallucination_heuristic
from src.eval.reranker import SimpleEmbeddingReranker

def to_profile_dict(profile: Any) -> Dict[str,Any]:
    if hasattr(profile, "dict"):
        return profile.dict()
    try:
        return dict(profile)
    except Exception:
        return {}

def load_evalset(path: str) -> List[Dict[str,Any]]:
    items = []
    with jsonlines.open(path, "r") as r:
        for obj in r:
            items.append(obj)
    return items

def maybe_rerank(docs: List[Dict[str,Any]], query: str, enabled: bool) -> List[Dict[str,Any]]:
    if not enabled:
        return docs
    rr = SimpleEmbeddingReranker()
    return rr.rerank(query, docs, text_key="text")

def evaluate(eval_path: str, out_dir: str, topk_list: List[int], use_reranker: bool, answer: bool) -> pd.DataFrame:
    eval_items = load_evalset(eval_path)
    retriever = get_retriever()

    rows = []
    for ex in eval_items:
        q    = ex["query"]
        it   = ex.get("intent")
        prof = to_profile_dict(ex.get("profile", {}))
        gold_ids  = ex.get("gold_doc_ids")
        gold_subs = ex.get("gold_answer_substrings")

        # 1) Retrieve (once)
        t0 = now_ms()
        docs_all = retriever(q, intent=it, profile=prof) or []
        t1 = now_ms()
        base_retrieval_ms = t1 - t0

        # Optional second-stage rerank
        docs_all = maybe_rerank(docs_all, q, enabled=use_reranker)

        # Precompute relevance ranks against the full list
        ranks = first_relevant_ranks(docs_all, gold_ids, gold_subs)

        for k in topk_list:
            docs_k = docs_all[:k]

            # Retrieval metrics
            rec = recall_at_k(ranks, k)
            rr  = mrr([r for r in ranks if r < k])

            # 2) Generate answer & measure latency (optional)
            ans_ms = None
            halluc = None
            ans_text = ""
            citations = None

            if answer:
                a0 = now_ms()
                result = compose_answer(q, it, docs_k, prof)
                a1 = now_ms()
                ans_ms = a1 - a0
                ans_text = (result or {}).get("message","")
                citations = (result or {}).get("citations", [])
                halluc = hallucination_heuristic(ans_text, citations, gold_subs)

            rows.append({
                "query": q,
                "intent": it,
                "k": k,
                "retrieval_ms": base_retrieval_ms,
                "answer_ms": ans_ms,
                "recall_at_k": rec,
                "mrr": rr,
                "hallucination": halluc,
                "used_reranker": use_reranker,
            })

    df = pd.DataFrame(rows)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    # Save per-query results
    perq_csv = str(Path(out_dir) / f"rag_eval_perquery_rerank-{int(use_reranker)}.csv")
    df.to_csv(perq_csv, index=False)

    # Aggregate + save summary
    summary = df.groupby(["k"]).agg({
        "retrieval_ms":"mean",
        "answer_ms":"mean",
        "recall_at_k":"mean",
        "mrr":"mean",
        "hallucination":"mean"
    }).reset_index()
    summ_csv = str(Path(out_dir) / f"rag_eval_summary_rerank-{int(use_reranker)}.csv")
    summary.to_csv(summ_csv, index=False)

    # Basic charts
    plt.figure()
    plt.plot(summary["k"], summary["recall_at_k"], marker="o")
    plt.xlabel("k"); plt.ylabel("Recall@k"); plt.title(f"Recall@k (reranker={use_reranker})")
    plt.tight_layout(); plt.savefig(Path(out_dir) / f"chart_recall_rerank-{int(use_reranker)}.png", dpi=160)

    plt.figure()
    plt.plot(summary["k"], summary["mrr"], marker="o")
    plt.xlabel("k"); plt.ylabel("MRR"); plt.title(f"MRR (reranker={use_reranker})")
    plt.tight_layout(); plt.savefig(Path(out_dir) / f"chart_mrr_rerank-{int(use_reranker)}.png", dpi=160)

    plt.figure()
    plt.plot(summary["k"], summary["retrieval_ms"], marker="o", label="retrieval")
    if "answer_ms" in summary and summary["answer_ms"].notna().any():
        plt.plot(summary["k"], summary["answer_ms"], marker="o", label="answer")
        plt.legend()
    plt.xlabel("k"); plt.ylabel("ms"); plt.title(f"Latency vs k (reranker={use_reranker})")
    plt.tight_layout(); plt.savefig(Path(out_dir) / f"chart_latency_rerank-{int(use_reranker)}.png", dpi=160)

    if "hallucination" in summary and summary["hallucination"].notna().any():
        plt.figure()
        plt.plot(summary["k"], summary["hallucination"], marker="o")
        plt.xlabel("k"); plt.ylabel("Hallucination rate"); plt.title(f"Hallucination vs k (reranker={use_reranker})")
        plt.tight_layout(); plt.savefig(Path(out_dir) / f"chart_halluc_rerank-{int(use_reranker)}.png", dpi=160)

    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval_path", default="backend/data/evalset.jsonl")
    parser.add_argument("--out_dir",   default="backend/reports")
    parser.add_argument("--k_list",    default="3,5,10")
    parser.add_argument("--reranker",  action="store_true")
    parser.add_argument("--with_answer", action="store_true", help="Also call compose_answer to time + hallucination")
    args = parser.parse_args()

    k_list = [int(x) for x in str(args.k_list).split(",") if x.strip()]
    evaluate(args.eval_path, args.out_dir, k_list, use_reranker=args.reranker, answer=args.with_answer)
