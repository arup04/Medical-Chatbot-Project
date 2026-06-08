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
embeddings = download_hugging_face_embeddings()
index_name = "medibot"
vector_store = get_vector_store(index_name=index_name, embeddings=embeddings)
rag_chain = create_rag_chain(vector_store=vector_store)

async def stream_response(msg: str):
    try:
        # Use LangChain astream to generate response chunks asynchronously
        async for chunk in rag_chain.astream({"input": msg}):
            if "context" in chunk:
                # Extract documents and metadata
                docs = []
                for doc in chunk["context"]:
                    docs.append({
                        "page_content": doc.page_content,
                        "metadata": doc.metadata
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
