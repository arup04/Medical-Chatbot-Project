import os
import sys
from src.logger import logging
from src.exception import CustomException
from langchain_groq import ChatGroq
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.prompt import system_prompt, contextualize_q_system_prompt

def create_rag_chain(retriever, model_name: str = None):
    """
    Creates and returns a history-aware retrieval-augmented generation (RAG) chain.
    """
    try:
        logging.info("Initializing RAG pipeline components...")
        
        # Determine model name
        if not model_name:
            model_name = os.getenv("GROQ_MODEL_NAME", "openai/gpt-oss-120b")
        
        logging.info(f"Using Groq Chat Model: {model_name}")
        chat_model = ChatGroq(model=model_name)
        
        # 1. Create a prompt for contextualizing the question
        logging.info("Creating reformulation prompt for history-aware retriever...")
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        # 2. Create history-aware retriever
        logging.info("Creating history-aware retriever...")
        history_aware_retriever = create_history_aware_retriever(
            chat_model, retriever, contextualize_q_prompt
        )
        
        # 3. Configure final system answer prompt
        logging.info("Creating ChatPromptTemplate from system prompt structure...")
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        # 4. Combine documents into stuff chain
        logging.info("Combining documents with LLM using stuff documents chain...")
        question_answer_chain = create_stuff_documents_chain(chat_model, prompt)
        
        # 5. Create full history-aware retrieval chain
        logging.info("Constructing final RAG retrieval chain...")
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        
        logging.info("RAG chain successfully constructed.")
        return rag_chain
    except Exception as e:
        logging.error("Error occurred while creating RAG chain")
        raise CustomException(e, sys)
