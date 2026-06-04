import sys
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.logger import logging
from src.exception import CustomException

def filter_to_minimal_docs(docs: List[Document]) -> List[Document]:
    """
    Given a list of Document objects, return a new list of Document objects
    containing only 'source' in metadata and the original page_content.
    """
    try:
        logging.info("Starting filtering of documents to minimal structure.")
        minimal_docs: List[Document] = []
        for doc in docs:
            src = doc.metadata.get("source")
            minimal_docs.append(
                Document(
                    page_content=doc.page_content,
                    metadata={"source": src}
                )
            )
        logging.info(f"Successfully filtered {len(minimal_docs)} documents.")
        return minimal_docs
    except Exception as e:
        logging.error("Error occurred during document filtering")
        raise CustomException(e, sys)

def text_split(minimal_docs: List[Document]) -> List[Document]:
    """
    Splits documents into smaller text chunks.
    """
    try:
        logging.info("Starting text splitting on documents.")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
        text_chunks = text_splitter.split_documents(minimal_docs)
        logging.info(f"Successfully split documents into {len(text_chunks)} chunks.")
        return text_chunks
    except Exception as e:
        logging.error("Error occurred during text splitting")
        raise CustomException(e, sys)
