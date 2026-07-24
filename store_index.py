import os
from dotenv import load_dotenv
from src.ingestion import download_from_s3, load_pdf_file
from src.preprocessing import filter_to_minimal_docs, text_split
from src.vector_store import download_hugging_face_embeddings, init_vector_store
from src.logger import logging

load_dotenv()

def main():
    # S3 configurations from env
    bucket_name = os.getenv("AWS_BUCKET_NAME")
    file_key = os.getenv("AWS_FILE_KEY")
    local_data_dir = "Data"
    local_pdf_path = os.path.join(local_data_dir, "Medical_book.pdf")

    # Ingestion - Download from S3 if configured
    if bucket_name and file_key:
        logging.info("S3 configuration found. Attempting download from S3...")
        try:
            download_from_s3(bucket_name, file_key, local_pdf_path)
        except Exception as e:
            logging.error(f"S3 download failed, falling back to local files: {e}")
    else:
        logging.info("S3 configuration (AWS_BUCKET_NAME / AWS_FILE_KEY) not set in env. Using local data directory.")

    # Load pdf files
    logging.info("Loading PDF documents...")
    extracted_doc = load_pdf_file(data_path=local_data_dir)

    # Preprocessing
    logging.info("Preprocessing documents...")
    minimal_docs = filter_to_minimal_docs(extracted_doc)
    text_chunks = text_split(minimal_docs)

    # Cache preprocessed text chunks to a local JSON file for BM25 loading
    import json
    chunks_data = []
    for chunk in text_chunks:
        chunks_data.append({
            "page_content": chunk.page_content,
            "metadata": chunk.metadata
        })
    cache_path = "evaluation/preprocessed_chunks.json"
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(chunks_data, f, ensure_ascii=False, indent=2)
    logging.info(f"Cached {len(chunks_data)} chunks to {cache_path} for BM25 retrieval.")

    # Vector Store
    logging.info("Initializing/Connecting to vector store...")
    embeddings = download_hugging_face_embeddings()
    index_name = "medibot"
    docsearch = init_vector_store(index_name, text_chunks, embeddings)
    logging.info("Store index process completed.")

if __name__ == "__main__":
    main()
