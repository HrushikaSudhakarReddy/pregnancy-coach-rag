# Pregnancy Coach (Local RAG Chatbot)

A **privacy-first pregnancy coach** that runs completely **locally on your laptop**.
The assistant answers questions about **workouts, nutrition, hydration, vitamins, and safety** during pregnancy using a **Retrieval-Augmented Generation (RAG)** pipeline over a curated knowledge base.

⚠️ **Not medical advice.** Educational content only. Always consult your obstetric provider.

---

# Features

### Fully Local AI Stack

* **LLM:** Ollama (`llama3.2:1b` default, optional `llama3:8b`)
* **Embeddings:** `nomic-embed-text`
* **Vector Database:** ChromaDB (local persistent storage)

### Backend (FastAPI)

* `/chat` endpoint for RAG-based responses
* `/healthz` health check
* Clean conversational output formatting
* Profile-aware responses (trimester, activity level, diet, allergies, conditions)

### Frontend (Next.js + Tailwind)

* Interactive chat UI
* Pregnancy profile sidebar
* Soft **baby-pink themed design**
* Markdown rendering (`react-markdown`, `remark-gfm`)
* Framer Motion animations

### Knowledge Base

Curated pregnancy information stored as `.md` files:

* workouts
* strength training
* yoga & mobility
* nutrition
* hydration
* vitamins
* trimester guidance
* food safety

---

# Tech Stack

### AI / ML

* Ollama (LLM inference)
* ChromaDB (vector retrieval)
* Local embeddings (`nomic-embed-text`)

### Backend

* Python 3.10+
* FastAPI
* Uvicorn

### Frontend

* Next.js 14
* React
* TailwindCSS v3
* Framer Motion
* Lucide Icons

### Markdown Rendering

* react-markdown
* remark-gfm

---

# Project Architecture

User Question
↓
Next.js Chat UI
↓
FastAPI Backend
↓
Intent + Safety Classifiers
↓
Chroma Vector Search
↓
Ollama LLM
↓
Final Response

---

# Quickstart

## 1️⃣ Install Ollama

Start Ollama:

```bash
ollama serve
```

Pull models:

```bash
ollama pull llama3.2:1b
ollama pull nomic-embed-text
```

Optional larger model:

```bash
ollama pull llama3:8b
```

---

# 2️⃣ Run Backend

```bash
cd backend

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
```

Build the vector database:

```bash
python -m scripts.index_kb
```

Start the API:

```bash
python -m uvicorn app:app --reload --port 8001
```

Test health endpoint:

```bash
curl http://127.0.0.1:8001/healthz
```

Expected response:

```json
{"ok": true}
```

---

# 3️⃣ Run Frontend

```bash
cd frontend

npm install

cp .env.example .env.local
```

Add backend URL:

```bash
echo "NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8001" > .env.local
```

Start frontend:

```bash
npm run dev
```

Open the app:

```
http://localhost:3000
```

---

# Example Questions

* "What exercises are safe during the second trimester?"
* "Give me a vegetarian pregnancy meal plan."
* "How much water should I drink at 24 weeks?"
* "What vitamins are recommended during pregnancy?"

---

# Safety Notice

This application provides **educational information only** and **does not replace professional medical advice**.

Always consult a **qualified healthcare provider** for medical guidance.
