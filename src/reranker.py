# src/reranker.py
from langchain.retrievers.document_compressors import FlashrankRerank
from langchain.retrievers import ContextualCompressionRetriever

def get_reranked_retriever(base_retriever, top_n: int = 3):
    """
    Wraps a base retriever with FlashRank cross-encoder reranking.
    """
    # By default, FlashrankRerank uses 'ms-marco-MiniLM-L-6-v2'
    compressor = FlashrankRerank(top_n=top_n)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=base_retriever
    )
    return compression_retriever
