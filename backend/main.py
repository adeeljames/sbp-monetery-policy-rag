from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from langchain_cohere import CohereEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from langchain_groq import ChatGroq
import cohere
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document

app = FastAPI(title="SBP Monetary Policy RAG Chatbot")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")

if not all([GROQ_API_KEY, COHERE_API_KEY, QDRANT_API_KEY, QDRANT_URL]):
    raise ValueError("Missing required environment variables")

# Initialize models
dense_embeddings = CohereEmbeddings(model="embed-english-v3.0", cohere_api_key=COHERE_API_KEY)
sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0, api_key=GROQ_API_KEY)
co = cohere.Client(COHERE_API_KEY)

# Connect to existing Qdrant collection
# Connect to existing Qdrant collection
vector_store = QdrantVectorStore.from_existing_collection(
    embedding=dense_embeddings,
    sparse_embedding=sparse_embeddings,
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    collection_name="mpr_report_hybrid",
    retrieval_mode=RetrievalMode.HYBRID,
)

# Document summary (pre-computed from notebook)
doc_summary = """The document is the Monetary Policy Report for August 2026, published by the State Bank of Pakistan (SBP). The report is structured into various chapters, boxes, and figures, providing an in-depth analysis of macroeconomic developments, risks to the outlook, and monetary policy considerations. The scope of the report includes discussions on inflation, global economic trends, and the SBP's policy stance, with contributions from the Monetary Policy Committee members. The report aims to provide a comprehensive overview of the current economic situation and the SBP's monetary policy decisions."""

# Chat memory (in-memory for simplicity)
chat_history = []

class QuestionRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class AnswerResponse(BaseModel):
    answer: str
    sources: List[str]
    query_type: str

def format_recent_history(max_turns=3):
    recent = chat_history[-max_turns:]
    if not recent:
        return "(no previous conversation)"
    
    lines = []
    for turn in recent:
        lines.append(f"Q: {turn['question']}\nA: {turn['answer']}")
    return "\n\n".join(lines)

def classify_query(question):
    """Returns 'META' or 'FACTUAL'."""
    router_prompt = f"""Classify the question below as exactly one word: META or FACTUAL.

META = the question asks about the document as a whole (its purpose, structure, authors, what it covers).
FACTUAL = the question asks for a specific fact, number, projection, or detail from inside the document.

Question: {question}

Answer with one word only:"""
    
    result = llm.invoke(router_prompt).content.strip().upper()
    if "META" in result:
        return "META"
    return "FACTUAL"

def hybrid_search_and_rerank(question, k_search=15, k_final=5):
    """Runs hybrid search, then reranks the results."""
    candidates = vector_store.similarity_search(question, k=k_search)
    
    if not candidates:
        return []
    
    candidate_texts = [doc.page_content for doc in candidates]
    
    reranked = co.rerank(
        model="rerank-english-v3.0",
        query=question,
        documents=candidate_texts,
        top_n=min(k_final, len(candidate_texts)),
    )
    
    top_docs = [candidates[result.index] for result in reranked.results]
    return top_docs

@app.get("/")
async def root():
    return {"message": "SBP Monetary Policy RAG Chatbot API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/chat", response_model=AnswerResponse)
async def chat(request: QuestionRequest):
    try:
        query_type = classify_query(request.question)
        
        if query_type == "META":
            context = f"Document summary:\n{doc_summary}"
            sources = []
        else:
            top_docs = hybrid_search_and_rerank(request.question)
            context_parts = []
            sources = []
            for doc in top_docs:
                section = doc.metadata.get("h2") or doc.metadata.get("h1") or "Unknown section"
                content_type = doc.metadata.get("content_type", "text")
                context_parts.append(f"[Section: {section} | Type: {content_type}]\n{doc.page_content}")
                sources.append(f"{section} ({content_type})")
            context = "\n\n---\n\n".join(context_parts) if context_parts else "(no relevant chunks found)"
        
        recent_history = format_recent_history()
        
        prompt = f"""You are a helpful assistant answering questions about the State Bank of Pakistan's Monetary Policy Report.

If the question is a greeting or general conversational remark (like "hi", "hello", "how are you", "thanks"), respond briefly and politely, and mention that you're here to help answer questions about the report.

For questions about the report itself, use ONLY the context below to answer. If the answer isn't in the context, say you don't know — don't make things up.

Recent conversation:
{recent_history}

Context:
{context}

Question: {request.question}

Answer:"""
        
        answer = llm.invoke(prompt).content
        
        chat_history.append({"question": request.question, "answer": answer})
        
        # Keep only last 10 turns to avoid memory issues
        if len(chat_history) > 10:
            chat_history.pop(0)
        
        return AnswerResponse(
            answer=answer,
            sources=sources,
            query_type=query_type
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear-history")
async def clear_history():
    global chat_history
    chat_history = []
    return {"message": "Chat history cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
