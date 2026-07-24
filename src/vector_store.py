import os
import sys
from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from src.logger import logging
from src.exception import CustomException
from langchain_core.documents import Document

def download_hugging_face_embeddings():
    """
    Downloads Hugging Face embeddings.
    """
    try:
        logging.info("Downloading sentence-transformers/all-MiniLM-L6-v2 embeddings...")
        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        logging.info("Embeddings successfully loaded.")
        return embeddings
    except Exception as e:
        logging.error("Error occurred while downloading Hugging Face embeddings")
        raise CustomException(e, sys)

def init_vector_store(index_name: str, documents: List[Document], embeddings) -> PineconeVectorStore:
    """
    Initializes Pinecone index and upserts documents into it only if it's empty.
    """
    try:
        logging.info(f"Initializing Pinecone vector store. Index name: {index_name}")
        api_key = os.getenv('PINECONE_API_KEY')
        if not api_key:
            raise ValueError("PINECONE_API_KEY is not set in environment variables.")

        pc = Pinecone(api_key=api_key)

        index_exists = pc.has_index(index_name)
        if not index_exists:
            logging.info(f"Index {index_name} does not exist. Creating new index...")
            pc.create_index(
                name=index_name,
                dimension=384,
                metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
            logging.info(f"Index {index_name} successfully created.")
            has_vectors = False
        else:
            logging.info(f"Index {index_name} already exists. Checking if it contains vectors...")
            index_instance = pc.Index(index_name)
            stats = index_instance.describe_index_stats()
            total_vectors = stats.get('total_vector_count', 0)
            logging.info(f"Index stats: {stats}. Total vectors: {total_vectors}")
            has_vectors = total_vectors > 0

        if has_vectors:
            logging.info(f"Vectors already exist in index {index_name}. Skipping ingestion and connecting to existing store.")
            return get_vector_store(index_name, embeddings)
        else:
            logging.info("Index is empty. Uploading documents to Pinecone index...")
            docsearch = PineconeVectorStore.from_documents(
                documents=documents,
                index_name=index_name,
                embedding=embeddings,
            )
            logging.info("Documents successfully upserted to Pinecone.")
            return docsearch
    except Exception as e:
        logging.error("Error occurred while initializing vector store")
        raise CustomException(e, sys)

def get_vector_store(index_name: str, embeddings) -> PineconeVectorStore:
    """
    Returns an existing Pinecone vector store interface for retrieval.
    """
    try:
        logging.info(f"Loading Pinecone vector store for index: {index_name}")
        api_key = os.getenv('PINECONE_API_KEY')
        if not api_key:
            raise ValueError("PINECONE_API_KEY is not set in environment variables.")

        docsearch = PineconeVectorStore(
            index_name=index_name,
            embedding=embeddings,
            pinecone_api_key=api_key
        )
        logging.info("Successfully connected to Pinecone vector store.")
        return docsearch
    except Exception as e:
        logging.error("Error occurred while getting vector store reference")
        raise CustomException(e, sys)
