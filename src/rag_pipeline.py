import os
import sys
from src.logger import logging
from src.exception import CustomException
from langchain_groq import ChatGroq
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from src.prompt import system_prompt

def create_rag_chain(vector_store, model_name: str = None):
    """
    Creates and returns a retrieval-augmented generation (RAG) chain.
    """
    try:
        logging.info("Initializing RAG pipeline components...")
        
        # Determine model name
        if not model_name:
            model_name = os.getenv("GROQ_MODEL_NAME", "openai/gpt-oss-120b")
        
        logging.info(f"Using Groq Chat Model: {model_name}")
        chat_model = ChatGroq(model=model_name)
        
        # Configure retriever
        logging.info("Configuring vector store retriever...")
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        
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
        
        logging.info("RAG chain successfully constructed.")
        return rag_chain
    except Exception as e:
        logging.error("Error occurred while creating RAG chain")
        raise CustomException(e, sys)
