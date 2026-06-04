import os
import boto3
import sys
from src.logger import logging
from src.exception import CustomException
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader

def download_from_s3(bucket_name: str, file_key: str, download_path: str):
    """
    Downloads a file from an AWS S3 bucket.
    """
    try:
        # Check if file already exists
        if os.path.exists(download_path) and os.path.getsize(download_path) > 0:
            logging.info(f"File already exists locally at {download_path}. Skipping S3 download.")
            return download_path

        logging.info(f"Starting download from S3 bucket: {bucket_name}, file: {file_key}")
        s3 = boto3.client('s3')
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(download_path), exist_ok=True)
        
        s3.download_file(bucket_name, file_key, download_path)
        logging.info(f"Successfully downloaded file to: {download_path}")
        return download_path
    except Exception as e:
        logging.error("Error occurred while downloading from S3")
        raise CustomException(e, sys)

def load_pdf_file(data_path: str):
    """
    Loads all PDF documents from a given directory.
    """
    try:
        logging.info(f"Loading PDF files from directory: {data_path}")
        loader = DirectoryLoader(
            data_path,
            glob="*.pdf",
            loader_cls=PyPDFLoader,
            use_multithreading=True
        )
        documents = loader.load()
        logging.info(f"Successfully loaded {len(documents)} document pages.")
        return documents
    except Exception as e:
        logging.error("Error occurred while loading PDF documents")
        raise CustomException(e, sys)
