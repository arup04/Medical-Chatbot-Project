# app.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import json
import asyncio

# Modular pipeline imports
from src.vector_store import download_hugging_face_embeddings, get_vector_store
from src.rag_pipeline import create_rag_chain

# Initialize FastAPI app
app = FastAPI()

load_dotenv()

# Static & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Chatbot setup using modular pipeline
import os
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.documents import Document

embeddings = download_hugging_face_embeddings()
index_name = "medibot"
vector_store = get_vector_store(index_name=index_name, embeddings=embeddings)

# 1. Load cached chunks for local BM25 sparse index
chunks_path = "evaluation/preprocessed_chunks.json"
cached_docs = []
if os.path.exists(chunks_path):
    try:
        with open(chunks_path, "r", encoding="utf-8") as f:
            cached_data = json.load(f)
        cached_docs = [Document(page_content=d["page_content"], metadata=d["metadata"]) for d in cached_data]
    except Exception as e:
        print(f"Failed to load cached chunks: {e}")

from src.hybrid_retriever import HybridThresholdRetriever

# 2. Build retrievers
pinecone_retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold", 
    search_kwargs={"score_threshold": 0.78, "k": 6}
)

if cached_docs:
    bm25_retriever = BM25Retriever.from_documents(cached_docs)
    bm25_retriever.k = 6
    # Combine BM25 sparse search and Pinecone dense search
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, pinecone_retriever],
        weights=[0.5, 0.5]
    )
    base_retriever = HybridThresholdRetriever(
        ensemble_retriever=ensemble_retriever,
        pinecone_retriever=pinecone_retriever
    )
else:
    base_retriever = pinecone_retriever

from src.reranker import get_reranked_retriever
retriever = get_reranked_retriever(base_retriever, top_n=3)

# 3. Create the RAG chain
rag_chain = create_rag_chain(retriever=retriever)

async def stream_response(msg: str):
    try:
        # Use LangChain astream to generate response chunks asynchronously
        async for chunk in rag_chain.astream({"input": msg}):
            if "context" in chunk:
                # Extract documents and metadata
                docs = []
                for doc in chunk["context"]:
                    clean_metadata = {}
                    for k, v in doc.metadata.items():
                        if hasattr(v, "item"): # Convert numpy types to native Python types
                            clean_metadata[k] = v.item()
                        else:
                            clean_metadata[k] = v
                    docs.append({
                        "page_content": doc.page_content,
                        "metadata": clean_metadata
                    })
                yield f"[CONTEXT] {json.dumps(docs)}\n"
            if "answer" in chunk:
                yield f"[ANSWER] {chunk['answer']}\n"
        yield "[DONE]\n"
    except Exception as e:
        yield f"[ERROR] {str(e)}\n"

# Routes
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/get")
async def chat(msg: str = Form(...)):
    # Stream the tokens and contexts back using a StreamingResponse
    return StreamingResponse(stream_response(msg), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
