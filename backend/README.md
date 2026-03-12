# Backend (Ollama + ChromaDB)

Install Ollama (https://ollama.com/download), run `ollama serve`, then pull models:
```
ollama pull llama3:8b
ollama pull nomic-embed-text
```

Run backend:
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/index_kb.py
uvicorn app:app --reload --port 8000
```
