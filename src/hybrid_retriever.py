# src/hybrid_retriever.py
import os
import sys
import json
from typing import List, Optional
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from src.logger import logging
from src.exception import CustomException


class HybridThresholdRetriever(BaseRetriever):
    """
    Retriever that uses a thresholded dense retriever as a domain gatekeeper.
    If the query passes the dense threshold, it runs ensemble hybrid retrieval (BM25 + Dense).
    Otherwise, returns an empty document list (out-of-domain query).
    """
    ensemble_retriever: EnsembleRetriever
    pinecone_retriever: BaseRetriever

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        # 1. Run pinecone retriever first to check for threshold matches
        dense_docs = self.pinecone_retriever.invoke(
            query, 
            config={"callbacks": run_manager.get_child()} if run_manager else None
        )
        if not dense_docs:
            # If no dense document meets the threshold, treat query as out-of-domain
            return []
        
        # 2. If matches exist, get ensemble results (BM25 + Pinecone)
        return self.ensemble_retriever.invoke(
            query, 
            config={"callbacks": run_manager.get_child()} if run_manager else None
        )

    async def _aget_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        # Async implementation for streaming RAG pipelines
        dense_docs = await self.pinecone_retriever.ainvoke(
            query, 
            config={"callbacks": run_manager.get_child()} if run_manager else None
        )
        if not dense_docs:
            return []
        return await self.ensemble_retriever.ainvoke(
            query, 
            config={"callbacks": run_manager.get_child()} if run_manager else None
        )


DEFAULT_CHUNKS_PATH = os.path.join("Data", "preprocessed_chunks.json")


def save_cached_chunks(chunks: List[Document], cache_path: str = DEFAULT_CHUNKS_PATH) -> None:
    """
    Saves document chunks to a JSON file in the Data/ folder for fast local BM25 index initialization.
    """
    try:
        logging.info(f"Saving {len(chunks)} preprocessed chunks to cache at '{cache_path}'...")
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        chunks_data = [
            {"page_content": chunk.page_content, "metadata": chunk.metadata}
            for chunk in chunks
        ]
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(chunks_data, f, ensure_ascii=False, indent=2)
        logging.info(f"Successfully cached {len(chunks_data)} chunks to {cache_path} for BM25 retrieval.")
    except Exception as e:
        logging.error("Error occurred while saving cached chunks for BM25")
        raise CustomException(e, sys)


def load_cached_chunks(cache_path: str = DEFAULT_CHUNKS_PATH) -> List[Document]:
    """
    Loads cached document chunks from the JSON file in the Data/ folder for the BM25 index.
    """
    try:
        if not os.path.exists(cache_path):
            logging.warning(f"Cached chunks file not found at '{cache_path}'. BM25 sparse index will be skipped.")
            return []

        logging.info(f"Loading cached chunks from '{cache_path}' for BM25 sparse index...")
        with open(cache_path, "r", encoding="utf-8") as f:
            cached_data = json.load(f)
        docs = [Document(page_content=d["page_content"], metadata=d.get("metadata", {})) for d in cached_data]
        logging.info(f"Successfully loaded {len(docs)} cached chunks from '{cache_path}'.")
        return docs
    except Exception as e:
        logging.error(f"Failed to load cached chunks from '{cache_path}': {e}")
        return []


def get_bm25_retriever(documents: List[Document], k: int = 6) -> Optional[BM25Retriever]:
    """
    Initializes and returns a BM25Retriever from the given document chunks.
    """
    try:
        if not documents:
            return None
        logging.info(f"Building BM25Retriever with {len(documents)} chunks (k={k})...")
        bm25_retriever = BM25Retriever.from_documents(documents)
        bm25_retriever.k = k
        return bm25_retriever
    except Exception as e:
        logging.error("Error initializing BM25Retriever")
        raise CustomException(e, sys)


def get_hybrid_retriever(
    vector_store,
    chunks_path: str = DEFAULT_CHUNKS_PATH,
    score_threshold: float = 0.78,
    k: int = 6,
    weights: list = [0.5, 0.5]
) -> BaseRetriever:
    """
    Builds and returns the Stage 3 Hybrid Retriever combining BM25 sparse search
    and Pinecone dense search with similarity score threshold gating.
    """
    try:
        logging.info(f"Creating Pinecone dense retriever (score_threshold={score_threshold}, k={k})...")
        pinecone_retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"score_threshold": score_threshold, "k": k}
        )

        cached_docs = load_cached_chunks(chunks_path)
        if cached_docs:
            bm25_retriever = get_bm25_retriever(cached_docs, k=k)
            if bm25_retriever:
                logging.info(f"Creating EnsembleRetriever with weights={weights}...")
                ensemble_retriever = EnsembleRetriever(
                    retrievers=[bm25_retriever, pinecone_retriever],
                    weights=weights
                )
                logging.info("Wrapping in HybridThresholdRetriever...")
                return HybridThresholdRetriever(
                    ensemble_retriever=ensemble_retriever,
                    pinecone_retriever=pinecone_retriever
                )

        logging.warning("Falling back to pure Pinecone retriever as cached chunks were not available.")
        return pinecone_retriever
    except Exception as e:
        logging.error("Error occurred while constructing hybrid retriever")
        raise CustomException(e, sys)

