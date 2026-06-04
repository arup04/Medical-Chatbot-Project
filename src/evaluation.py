import os
import sys
import pandas as pd
from datasets import Dataset
from ragas import evaluate, RunConfig
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from langchain_groq import ChatGroq
from langchain_core.rate_limiters import InMemoryRateLimiter
from src.logger import logging
from src.exception import CustomException

def evaluate_rag_pipeline(data_list: list, embeddings, model_name: str = None) -> pd.DataFrame:
    """
    Evaluates the RAG pipeline using RAGAS metrics.
    
    data_list should be a list of dictionaries, each containing:
      - 'question' / 'user_input'
      - 'answer' / 'response'
      - 'contexts' / 'retrieved_contexts'
      - 'ground_truth' / 'reference'
    """
    try:
        logging.info("Preparing dataset for RAGAS evaluation...")
        dataset = Dataset.from_list(data_list)
        
        # Configure model
        if not model_name:
            model_name = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
            
        logging.info(f"Initializing ChatGroq with model: {model_name}")
        
        # Initialize Rate Limiter to prevent 429 rate limit errors on Groq free tiers
        rate_limiter = InMemoryRateLimiter(
            requests_per_second=0.08,  # Space requests out (1 every ~12 seconds)
            check_every_n_seconds=0.1,
            max_bucket_size=1
        )
        
        eval_llm = ChatGroq(
            model=model_name,
            rate_limiter=rate_limiter
        )
        
        # Bind LLM and local embeddings to RAGAS metrics
        logging.info("Binding LLM and embeddings to RAGAS metrics...")
        metrics = [faithfulness, answer_relevancy, context_precision, context_recall]
        for metric in metrics:
            metric.llm = eval_llm
            if hasattr(metric, "embeddings"):
                metric.embeddings = embeddings
                
        # Enforce sequential execution via RunConfig
        run_config = RunConfig(
            max_workers=1,
            timeout=60
        )
        
        logging.info("Executing RAGAS evaluation run...")
        result = evaluate(
            dataset=dataset,
            metrics=metrics,
            run_config=run_config,
            raise_exceptions=True
        )
        
        logging.info("RAGAS evaluation successfully finished.")
        return result.to_pandas()
        
    except Exception as e:
        logging.error("Error occurred during RAGAS evaluation process")
        raise CustomException(e, sys)
