# app.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

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

# Routes
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/get")
async def chat(msg: str = Form(...)):
    response = rag_chain.invoke({"input": msg})
    return JSONResponse({"answer": response["answer"]})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
