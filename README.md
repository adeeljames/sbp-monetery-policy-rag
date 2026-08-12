# SBP Monetary Policy RAG Chatbot

A sophisticated RAG-based chatbot for the State Bank of Pakistan's Monetary Policy Report (August 2026).

## Features

- **Advanced RAG Pipeline**: Uses Docling for table-aware PDF parsing
- **Hybrid Search**: Combines dense (Cohere) and sparse (BM25) embeddings
- **Query Routing**: Intelligently routes meta vs factual questions
- **Reranking**: Cohere rerank for improved relevance
- **Chat Memory**: Maintains conversation context
- **Source Citations**: Provides document sources for answers

## Tech Stack

- **Backend**: FastAPI
- **Frontend**: Beautiful HTML/CSS chat interface
- **PDF Parsing**: Docling
- **Embeddings**: Cohere (dense) + FastEmbed (sparse)
- **Vector Database**: Qdrant Cloud (hybrid mode)
- **LLM**: Groq (Llama 3.3 70B)
- **Reranking**: Cohere Rerank v3
- **Framework**: LangChain

## Deployment Instructions

### 1. Deploy Backend to Render

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure the service:
   - **Name**: `sbp-rag-backend`
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or Starter for better performance)
6. Add Environment Variables:
   - `GROQ_API_KEY`: Your Groq API key
   - `COHERE_API_KEY`: Your Cohere API key
   - `QDRANT_API_KEY`: Your Qdrant API key
   - `QDRANT_URL`: Your Qdrant Cloud URL
7. Click "Deploy"

### 2. Deploy Frontend to Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Static Site"
3. Connect your GitHub repository
4. Configure the site:
   - **Name**: `sbp-rag-frontend`
   - **Build Command**: (leave empty)
   - **Publish Directory**: `.`
   - **Plan**: Free
5. After deployment, update the `API_URL` in `index.html`:
   - Replace `https://YOUR_BACKEND_URL.onrender.com` with your actual backend URL

### 3. Environment Variables

Make sure your `.env` file contains:
```
GROQ_API_KEY=your_groq_key
COHERE_API_KEY=your_cohere_key
QDRANT_API_KEY=your_qdrant_key
QDRANT_URL=your_qdrant_url
```

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the backend:
```bash
uvicorn main:app --reload
```

3. Open `index.html` in your browser

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /chat` - Chat endpoint
  - Body: `{"question": "your question"}`
  - Response: `{"answer": "...", "sources": [...], "query_type": "META/FACTUAL"}`
- `POST /clear-history` - Clear chat history

## Credits

Made with ❤️ by [@Muhammad Adil AI](https://www.linkedin.com/in/muhammad-adil-ai)

Built with FastAPI, Docling, Cohere, Qdrant, Groq & LangChain
