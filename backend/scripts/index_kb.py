
from pathlib import Path
from typing import List
from ollama import Client
from config import OLLAMA_HOST, OLLAMA_EMBED_MODEL
from src.rag.chroma_store import get_collection

KB_DIR = Path(__file__).resolve().parents[1] / "kb"

def chunk_text(text: str, max_chars: int = 1200) -> List[str]:
    chunks, buf = [], []
    total = 0
    for line in text.splitlines():
        if total + len(line) > max_chars and buf:
            chunks.append("\n".join(buf)); buf, total = [], 0
        buf.append(line); total += len(line) + 1
    if buf: chunks.append("\n".join(buf))
    return chunks

def embed(client: Client, texts: List[str]) -> List[List[float]]:
    out = []
    for t in texts:
        out.append(client.embeddings(model=OLLAMA_EMBED_MODEL, prompt=t)["embedding"])
    return out

def main():
    client = Client(host=OLLAMA_HOST)
    col = get_collection("pregnancy_kb")
    ids, docs, metas, vecs = [], [], [], []
    for md in KB_DIR.glob("*.md"):
        text = md.read_text(encoding="utf-8")
        chunks = chunk_text(text)
        embs = embed(client, chunks)
        for i, (c, v) in enumerate(zip(chunks, embs)):
            ids.append(f"{md.stem}-{i}")
            docs.append(c)
            metas.append({"source": str(md)})
            vecs.append(v)
    if ids:
        col.upsert(ids=ids, documents=docs, embeddings=vecs, metadatas=metas)
    print(f"Upserted {len(ids)} chunks into Chroma.")

if __name__ == "__main__":
    main()
