<div align="center">

# 🏦 SBP Monetary Policy RAG Chatbot

### Ask questions about the State Bank of Pakistan's Monetary Policy Report — get grounded, cited answers.

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Try_it_now-2ea44f?style=for-the-badge)](https://sbp-monetery-policy.onrender.com/)
[![API](https://img.shields.io/badge/⚡_API-FastAPI_Backend-009688?style=for-the-badge)](https://sbp-mpr.onrender.com/)

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-Orchestration-1C3C3C?style=flat-square&logo=langchain&logoColor=white)](https://www.langchain.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Hybrid_Search-DC244C?style=flat-square&logo=qdrant&logoColor=white)](https://qdrant.tech/)
[![Cohere](https://img.shields.io/badge/Cohere-Embeddings_%2B_Rerank-39594C?style=flat-square)](https://cohere.com/)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-F55036?style=flat-square)](https://groq.com/)
[![Docling](https://img.shields.io/badge/Docling-Table--Aware_Parsing-4B32C3?style=flat-square)](https://github.com/DS4SD/docling)

<br/>

<a href="https://www.linkedin.com/in/muhammadadeelai/">
  <img src="https://img.shields.io/badge/LinkedIn-Muhammad_Adeel-0A66C2?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn: muhammadadeelai" />
</a>

</div>

---

## 💡 What this is

A Retrieval-Augmented Generation (RAG) chatbot built over the **State Bank of Pakistan's Monetary Policy Report (August 2026)** — a dense, table-heavy 33-page central bank document covering inflation targets, GDP projections, fiscal policy, and macroeconomic risk analysis.

Most "chat with your PDF" projects fall over on documents like this, because the value is locked inside tables and multi-column layouts that naive text extraction mangles. This project was built specifically to handle that:

- **Tables survive intact** — extracted with a layout-aware parser, not scraped as loose text
- **Both "what does this document say" and "what's this document about"** are answered correctly, via a routing step, not just retrieval
- **Every answer cites its source section**, so you can verify it against the report yourself

<br/>

## 🖥️ Live Demo

| | |
|---|---|
| 💬 **Chat UI** | [sbp-monetery-policy.onrender.com](https://sbp-monetery-policy.onrender.com/) |
| ⚙️ **API** | [sbp-mpr.onrender.com](https://sbp-mpr.onrender.com/) |

> ⏳ Hosted on Render's free tier — the backend spins down when idle, so the first message after a while may take **30-60 seconds** to wake up. Totally normal, just give it a moment.

<br/>

## 🧠 How it works

```
┌─────────────────────┐
│  MPR PDF (33 pages)  │
└──────────┬───────────┘
           │  Docling (table-structure aware, ACCURATE mode)
           ▼
┌─────────────────────────────┐
│  Markdown with real tables  │
└──────────┬───────────────────┘
           │  Section-aware, table-preserving chunking
           ▼
┌─────────────────────────────┐
│   84 chunks (9 kept as       │
│   intact tables)             │
└──────────┬───────────────────┘
           │  Cohere dense embeddings + FastEmbed sparse (BM25)
           ▼
┌─────────────────────────────┐
│   Qdrant Cloud — hybrid      │
│   vector index                │
└──────────┬───────────────────┘
           │
     ┌─────┴──────┐
     │   Query     │
     │  Router     │──── META (about the doc) ──────┐
     └─────┬──────┘                                  │
           │ FACTUAL                                 │
           ▼                                          ▼
 Hybrid search (top 15)                    Cached document summary
           │
           ▼
 Cohere Rerank (top 5)
           │
           ▼
┌─────────────────────────────┐
│  Groq — Llama 3.3 70B         │
│  + chat memory (last 3 turns)│
└──────────┬───────────────────┘
           │
           ▼
    Answer + cited sources
```

### Why these specific choices

| Decision | Reasoning |
|---|---|
| **Docling over plain PDF text extraction** | This report's most important numbers live in tables (inflation targets, GDP projections, oil price assumptions). A naive extractor scrambles these; Docling's layout model keeps rows and columns intact. |
| **Table-preserving chunking** | A chunker that blindly splits every 1000 characters will cut a table in half. This pipeline detects table blocks and keeps them as single, untouched chunks. |
| **Hybrid search (dense + sparse)**, not dense-only | The document is full of acronyms and exact figures (`CAB`, `LSM`, `WRT`, `Table 2`). Dense embeddings alone are great at paraphrase matching but can miss exact-term queries — sparse (BM25-style) search catches those. |
| **Cohere Rerank** on top of hybrid search | Vector similarity gets you a decent shortlist; reranking re-scores that shortlist against the actual question, which measurably improves what reaches the LLM. |
| **Query router (META vs FACTUAL)** | "What is this report about?" and "What's the FY27 CAB projection?" need fundamentally different retrieval strategies — one needs a document overview, the other needs precise, reranked chunks. |
| **Ingestion separated from serving** | The PDF is parsed and uploaded to Qdrant **once**, offline. The deployed backend only ever queries — it doesn't re-parse or re-embed on every request or every deploy. |

<br/>

## 🛠️ Tech stack

| Layer | Tool |
|---|---|
| PDF parsing | [Docling](https://github.com/DS4SD/docling) (table-structure recognition, ACCURATE mode) |
| Orchestration | [LangChain](https://www.langchain.com/) |
| Dense embeddings | [Cohere](https://cohere.com/) `embed-english-v3.0` |
| Sparse embeddings | [FastEmbed](https://github.com/qdrant/fastembed) (BM25) |
| Vector database | [Qdrant Cloud](https://qdrant.tech/) — hybrid dense + sparse |
| Reranking | Cohere Rerank `v3` |
| LLM | [Groq](https://groq.com/) — Llama 3.3 70B |
| Backend | [FastAPI](https://fastapi.tiangolo.com/) |
| Frontend | Hand-built HTML/CSS/JS chat interface |
| Hosting | [Render](https://render.com/) (backend web service + static frontend) |

<br/>

## 📁 Repository structure

```
.
├── backend/
│   ├── main.py              # FastAPI app — /chat, /health endpoints
│   ├── requirements.txt
│   └── nixpacks.toml
├── frontend/
│   └── index.html           # Chat UI (vanilla HTML/CSS/JS)
├── notebook/
│   └── mpr_rag_prototype.ipynb   # Original Colab prototype — ingestion + RAG pipeline
└── README.md
```

<br/>

## ✨ Features

- 📊 **Table-aware parsing** — inflation targets, GDP tables, and fiscal projections stay structured
- 🔍 **Hybrid retrieval** — semantic + keyword search combined
- 🎯 **Reranking** — Cohere Rerank refines results before they reach the LLM
- 🧭 **Query routing** — meta questions and factual questions are handled differently, on purpose
- 💬 **Chat memory** — follow-up questions like "and what about FY26?" work
- 📎 **Source citations** — every answer names the section it came from
- 🖤 **Clean, purpose-built UI** — not a default chat template

<br/>

## 🚀 Running locally

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
# just open frontend/index.html in your browser
# (point API_URL inside it at http://localhost:8000)
```

Environment variables needed (`.env` or exported):
```
GROQ_API_KEY=
COHERE_API_KEY=
QDRANT_API_KEY=
QDRANT_URL=
```

For full deployment steps (Render, ingestion, environment setup), see [`DEPLOYMENT.md`](./DEPLOYMENT.md).

<br/>

## 📡 API reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | `GET` | Root / health ping |
| `/health` | `GET` | Health check |
| `/chat` | `POST` | `{"question": "..."}` → `{"answer": "...", "sources": [...], "query_type": "META \| FACTUAL"}` |
| `/clear-history` | `POST` | Clears server-side chat memory |

<br/>

---

<div align="center">

Built by **Muhammad Adeel**

[![LinkedIn](https://img.shields.io/badge/Connect_on_LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/muhammadadeelai/)

</div>
