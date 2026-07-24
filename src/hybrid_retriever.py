# src/hybrid_retriever.py
from typing import List
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain.retrievers import EnsembleRetriever

class HybridThresholdRetriever(BaseRetriever):
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
            # If no dense document meets the threshold, we treat the query as out-of-domain
            return []
        
        # 2. If we have matches, get the ensemble results
        return self.ensemble_retriever.invoke(
            query, 
            config={"callbacks": run_manager.get_child()} if run_manager else None
        )

    async def _aget_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        # Async implementation
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
