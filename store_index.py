from dotenv import load_dotenv
import os
from pinecone import Pinecone, ServerlessSpec
from src.helper import load_pdf_file, text_split, download_hugging_face_embeddings, filter_to_minimal_docs
from langchain_pinecone import PineconeVectorStore

load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

extracted_doc = load_pdf_file(data = "Data/")
minimal_docs = filter_to_minimal_docs(extracted_doc)
text_chunks=text_split(minimal_docs)
embeddings = download_hugging_face_embeddings()

pc = Pinecone()

index_name = "medibot"

if not pc.has_index(index_name):
  pc.create_index(
    name=index_name,
    dimension=384,
    metric='cosine',
    spec=ServerlessSpec(cloud='aws', region='us-east-1')) 
  
index = pc.Index(index_name)

docsearch = PineconeVectorStore.from_documents(
    documents=text_chunks,
    index_name=index_name,
    embedding=embeddings, 
)
