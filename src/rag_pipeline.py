import os
import sys
from src.logger import logging
from src.exception import CustomException
from langchain_sarvam import ChatSarvam
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.prompt import system_prompt, contextualize_q_system_prompt


def create_rag_chain(retriever, model_name: str = None, temperature: float = 0.0, max_tokens: int = 4096):
    """
    Creates and returns a multi-turn, history-aware Retrieval-Augmented Generation (RAG) chain
    using ChatSarvam as the generator and LangChain's history-aware retriever.
    """
    try:
        logging.info("Initializing multi-turn RAG pipeline components with Sarvam AI...")
        
        # Determine model name
        if not model_name:
            model_name = os.getenv("SARVAM_MODEL_NAME", "sarvam-105b")
        
        logging.info(f"Using Sarvam Chat Model: {model_name}")
        chat_model = ChatSarvam(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # 1. Contextualize Question Prompt for Follow-up Inquiries
        logging.info("Building contextualize question prompt for multi-turn conversational retrieval...")
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])
        
        # 2. History-Aware Retriever
        history_aware_retriever = create_history_aware_retriever(
            chat_model, retriever, contextualize_q_prompt
        )
        
        # 3. Question-Answering Prompt with Chat History Placeholder
        logging.info("Creating ChatPromptTemplate with chat_history placeholder...")
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])
        
        # 4. Combine Documents Chain
        logging.info("Combining documents with LLM using stuff documents chain...")
        question_answer_chain = create_stuff_documents_chain(chat_model, qa_prompt)
        
        # 5. Full Multi-Turn Retrieval Chain
        logging.info("Constructing final history-aware RAG retrieval chain...")
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        
        logging.info("History-aware RAG chain successfully constructed with Sarvam AI.")
        return rag_chain
    except Exception as e:
        logging.error("Error occurred while creating history-aware RAG chain with Sarvam AI")
        raise CustomException(e, sys)
