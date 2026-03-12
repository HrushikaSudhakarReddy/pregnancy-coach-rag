# Pregnancy Coach (Local RAG Chatbot)

Privacy-first pregnancy coach that runs **fully locally** on your laptop. It answers questions about **workouts, meals, hydration, and vitamins** during pregnancy using a **retrieval-augmented generation (RAG)** pipeline over a curated knowledge base.

> **Not medical advice.** Educational content only — always consult your obstetric provider.

---

## Features

- **End-to-end local stack**
  - LLM via **Ollama** (`llama3.2:1b` by default; easy switch to `llama3:8b`)
  - **Embeddings:** `nomic-embed-text`
  - **Vector store:** **ChromaDB** (persisted on disk)
- **Backend (FastAPI)**
  - `/chat` endpoint with retrieval + clean, human-style answers (short paragraphs, bullets, light **bold**)
  - `/healthz` health check
  - Output polishing (real newlines; no code blocks/tables; no noisy object dumps)
  - Profile-aware responses (trimester, weeks, activity level, diet, allergies, restrictions, conditions)
- **Frontend (Next.js + Tailwind v3)**
  - Chat UI with **profile sidebar**
  - White theme with **baby-pink** accents; inputs are white with dark text
  - Optional **background image only behind the chat panel**
  - Markdown rendering via `react-markdown` + `remark-gfm`
- **Knowledge Base**
  - Curated `.md` files (workouts, strength, mobility, nutrition, vitamins, hydration, food safety, trimester tips, disclaimer)
  - Simple indexer script to (re)embed into Chroma

---

## Tech Stack

- **LLM & Embeddings:** Ollama (`llama3.2:1b`, `llama3:8b`), `nomic-embed-text`
- **Vector DB:** ChromaDB
- **Backend:** Python 3.10+, FastAPI, Uvicorn
- **Frontend:** Next.js 14, React, Tailwind CSS v3, Framer Motion, Lucide Icons
- **Markdown:** `react-markdown`, `remark-gfm`

---



## Quickstart
### 1) Ollama
```bash
ollama serve
ollama pull llama3.2:1b / ollama pull llama3:8b
ollama pull nomic-embed-text
```
### 2) Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m scripts.index_kb     # builds vector store from backend/kb/*.md
# embed the knowledge base (backend/kb/*.md)
python -m scripts.index_kb

# run API (port 8001)
python -m uvicorn app:app --reload --port 8001

# health (new terminal)
curl http://127.0.0.1:8001/healthz
# -> {"ok":true,"debug":true}
```
### 3) Frontend
```bash
cd ../frontend
npm install
echo "NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8001" > .env.local
cp .env.example .env.local
npm run dev
```

Open http://localhost:3000
