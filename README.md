# Pregnancy Coach — Local RAG AI Assistant

A **privacy-first AI assistant** that answers pregnancy-related questions about **nutrition, exercise, hydration, and vitamins** using a **Retrieval-Augmented Generation (RAG)** pipeline over a curated knowledge base.

The system runs **entirely locally**, combining **vector search, machine learning classifiers, and an LLM** to generate safe, structured responses.

⚠️ This project is for **educational purposes only** and does not replace professional medical advice.

---

# Project Overview

This project demonstrates how to build an **end-to-end AI application** that combines:

• **Machine learning classifiers** (intent detection & safety filtering)
• **Vector retrieval** using embeddings
• **Large language model generation**
• **FastAPI backend services**
• **Interactive Next.js frontend**

The assistant retrieves relevant information from a curated knowledge base and generates contextual answers tailored to a user's pregnancy profile.

---

# System Architecture

User Query
↓
Next.js Chat Interface
↓
FastAPI API Layer
↓
Intent Classification + Safety Filtering
↓
Vector Retrieval (ChromaDB + embeddings)
↓
LLM Response Generation (Ollama)
↓
Structured Answer Returned to User

---

# Key Data Science Components

### Intent Classification

A lightweight ML classifier determines the **user’s query intent** (nutrition, exercise, safety, vitamins, etc.) to guide retrieval and response generation.

### Safety Classification

A safety model flags **potentially risky medical queries**, ensuring the assistant responds cautiously.

### Retrieval-Augmented Generation (RAG)

Relevant documents are retrieved from a **vector database (ChromaDB)** using embeddings before generating responses with the language model.

### Knowledge Base

The RAG system uses a curated dataset of pregnancy guidance stored as structured Markdown files covering topics such as:

• nutrition
• hydration
• vitamins
• exercise safety
• trimester-specific guidance

---

# Technology Stack

### AI / Data Science

* Ollama (LLM inference)
* ChromaDB (vector database)
* nomic-embed-text (embeddings)
* Python ML pipeline for intent and safety classification

### Backend

* Python
* FastAPI
* Uvicorn

### Frontend

* Next.js
* React
* TailwindCSS
* Framer Motion

---

# Running the Project

### 1. Start Ollama

```bash
ollama serve
ollama pull llama3.2:1b
ollama pull nomic-embed-text
```

---

### 2. Start Backend

```bash
cd backend

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python -m scripts.index_kb
python -m uvicorn app:app --reload --port 8001
```

---

### 3. Start Frontend

```bash
cd frontend

npm install
echo "NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8001" > .env.local

npm run dev
```

Open:

```
http://localhost:3000
```

---

# Example Queries

• "What exercises are safe during the second trimester?"
• "How much water should I drink at 24 weeks?"
• "Give me a vegetarian pregnancy meal plan."
• "What vitamins are recommended during pregnancy?"

---

# Example Interface

Screenshots of the interface and model responses are shown below.

<!-- Add screenshots here -->

---

# Future Improvements

• Larger LLM models for higher quality responses
• Better evaluation metrics for retrieval accuracy
• Expanded knowledge base
• User personalization using long-term memory


