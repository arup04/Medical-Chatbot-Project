import os
import sys
from src.logger import logging
from src.exception import CustomException
from langchain_sarvam import ChatSarvam
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from src.prompt import system_prompt

def create_rag_chain(retriever, model_name: str = None, temperature: float = 0.0, max_tokens: int = 4096):
    """
    Creates and returns a retrieval-augmented generation (RAG) chain using ChatSarvam as the generator.
    """
    try:
        logging.info("Initializing RAG pipeline components with Sarvam AI...")
        
        # Determine model name
        if not model_name:
            model_name = os.getenv("SARVAM_MODEL_NAME", "sarvam-105b")
        
        logging.info(f"Using Sarvam Chat Model: {model_name}")
        chat_model = ChatSarvam(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Configure prompt
        logging.info("Creating ChatPromptTemplate from prompt structure...")
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])
        
        # Combine documents into stuff chain
        logging.info("Combining documents with LLM using stuff documents chain...")
        question_answer_chain = create_stuff_documents_chain(chat_model, prompt)
        
        # Create full retrieval chain
        logging.info("Constructing final RAG retrieval chain...")
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        
        logging.info("RAG chain successfully constructed with Sarvam AI.")
        return rag_chain
    except Exception as e:
        logging.error("Error occurred while creating RAG chain with Sarvam AI")
        raise CustomException(e, sys)
