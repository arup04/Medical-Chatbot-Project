import os
import json
import pandas as pd
from dotenv import load_dotenv
from src.vector_store import download_hugging_face_embeddings, get_vector_store
from src.rag_pipeline import create_rag_chain
from src.evaluation import evaluate_rag_pipeline
from src.logger import logging

load_dotenv()

def main():
    try:
        logging.info("Starting evaluation orchestration script...")

        # 1. Initialize RAG pipeline with Hybrid Search
        from langchain_community.retrievers import BM25Retriever
        from langchain.retrievers import EnsembleRetriever
        from langchain_core.documents import Document
        
        logging.info("Loading embeddings and connecting to vector store...")
        embeddings = download_hugging_face_embeddings()
        index_name = "medibot"
        vector_store = get_vector_store(index_name=index_name, embeddings=embeddings)
        
        # Load cached chunks for local BM25 sparse index
        chunks_path = "evaluation/preprocessed_chunks.json"
        cached_docs = []
        if os.path.exists(chunks_path):
            with open(chunks_path, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
            cached_docs = [Document(page_content=d["page_content"], metadata=d["metadata"]) for d in cached_data]
        
        from src.hybrid_retriever import HybridThresholdRetriever

        pinecone_retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold", 
            search_kwargs={"score_threshold": 0.78, "k": 3}
        )
        
        if cached_docs:
            bm25_retriever = BM25Retriever.from_documents(cached_docs)
            bm25_retriever.k = 3
            ensemble_retriever = EnsembleRetriever(
                retrievers=[bm25_retriever, pinecone_retriever],
                weights=[0.5, 0.5]
            )
            retriever = HybridThresholdRetriever(
                ensemble_retriever=ensemble_retriever,
                pinecone_retriever=pinecone_retriever
            )
            logging.info("Hybrid Search (EnsembleRetriever + HybridThresholdRetriever) successfully configured for evaluation.")
        else:
            retriever = pinecone_retriever
            logging.warning("Preprocessed chunks cache not found. Evaluation falling back to dense Pinecone retrieval.")
            
        rag_chain = create_rag_chain(retriever=retriever)

        # 2. Load evaluation dataset
        dataset_path = "evaluation/ragas_medical_evaluation_dataset.json"
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Evaluation dataset not found at {dataset_path}")
            
        logging.info(f"Loading dataset from {dataset_path}...")
        with open(dataset_path, "r", encoding="utf-8") as f:
            eval_data = json.load(f)

        # Limit to a small subset for safety on free-tier limits, but check if user wants full run
        run_full = os.getenv("RUN_FULL_EVALUATION", "false").lower() == "true"
        subset_limit = len(eval_data) if run_full else 3
        
        logging.info(f"Preparing to evaluate RAG pipeline on {subset_limit} questions...")
        test_subset = eval_data[:subset_limit]

        # 3. Generate answers and retrieve contexts from the RAG chain
        evaluation_samples = []
        for idx, item in enumerate(test_subset):
            question = item["question"]
            ground_truth = item["ground_truth"]
            
            logging.info(f"[{idx+1}/{subset_limit}] Processing question: '{question[:40]}...'")
            response = rag_chain.invoke({"input": question})
            
            generated_answer = response["answer"]
            retrieved_contexts = [doc.page_content for doc in response["context"]]
            
            # Map both sets of keys to be backward/forward compatible with RAGAS versions
            evaluation_samples.append({
                "question": question,
                "user_input": question,
                "answer": generated_answer,
                "response": generated_answer,
                "contexts": retrieved_contexts,
                "retrieved_contexts": retrieved_contexts,
                "ground_truth": ground_truth,
                "reference": ground_truth
            })

        # 4. Run RAGAS evaluation
        logging.info("Sending predictions to RAGAS evaluation module...")
        df_results = evaluate_rag_pipeline(evaluation_samples, embeddings)

        # 5. Save and display results
        output_csv = "evaluation/ragas_evaluation_results.csv"
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        df_results.to_csv(output_csv, index=False)
        logging.info(f"Evaluation results successfully saved to {output_csv}")

        print("\n=== RAGAS Evaluation Results Summary ===")
        print(df_results.to_string(index=False))
        
        # Calculate and show average scores
        metric_cols = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
        available_cols = [col for col in metric_cols if col in df_results.columns]
        
        if available_cols:
            print("\n=== Average RAGAS Scores ===")
            for col in available_cols:
                avg_score = df_results[col].mean()
                print(f"- {col.title()}: {avg_score:.4f}")
        print("========================================")

    except Exception as e:
        logging.error(f"Failed to complete RAG evaluation: {e}")
        raise e

if __name__ == "__main__":
    main()
