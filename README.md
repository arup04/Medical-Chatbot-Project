# 🩺 Medical Chatbot — Hybrid RAG Pipeline with FlashRank Reranking & Interactive UI

An end-to-end, production-ready **Medical AI Assistant** built with a multi-stage Retrieval-Augmented Generation (RAG) architecture. The system processes and indexes medical domain knowledge (e.g., the *Gale Encyclopedia of Medicine*), leveraging **Pinecone dense vector search**, **local BM25 sparse retrieval**, **FlashRank cross-encoder reranking**, **Groq LLM inference**, **FastAPI real-time streaming**, and continuous quality evaluation via the **RAGAS framework**.

> **Branch Note**: You are currently on the `reranking_improvements` branch, which introduces **FlashRank Cross-Encoder Contextual Compression & Reranking** on top of **Hybrid Search (Dense + Sparse)** and the **FastAPI Streaming Web UI**.

---

## 🌟 Key Features

- **⚡ FlashRank Cross-Encoder Reranking**: Integrates `FlashrankRerank` (`ms-marco-MiniLM-L-6-v2`) wrapped inside LangChain's `ContextualCompressionRetriever` (`src/reranker.py`) to re-score and select the top 3 most relevant context chunks from hybrid search candidate results (`k=6`), significantly boosting Context Precision.
- **🔀 Hybrid Search (Dense + Sparse)**: Combines dense semantic embeddings (`sentence-transformers/all-MiniLM-L6-v2`) with sparse keyword matching (`BM25Retriever`) via an `EnsembleRetriever` with balanced 50/50 weighting.
- **🎯 Dynamic Out-of-Domain Filtering**: Employs a custom `HybridThresholdRetriever` enforcing a dense Pinecone similarity threshold (`0.78`) to reject out-of-domain medical queries safely.
- **📡 Real-Time Token & Context Streaming**: FastAPI backend using `StreamingResponse` to broadcast live token streams (`[ANSWER]`) and retrieved source context metadata (`[CONTEXT]`).
- **🖥️ Interactive Web UI**: Custom dark-themed web frontend (`templates/chat.html`, `static/style.css`, `static/script.js`) featuring real-time message streaming, source citations, and context drawer.
- **☁️ Cloud Ingestion Pipeline**: Automated AWS S3 PDF downloading via `boto3` with local storage fallback (`Data/Medical_book.pdf`).
- **📊 RAGAS Quality Evaluation**: Production evaluation suite measuring **Faithfulness**, **Answer Relevancy**, **Context Precision**, and **Context Recall** with built-in `InMemoryRateLimiter`.

---

## 🛠️ System Architecture

```mermaid
graph TD
    subgraph Data Ingestion & Indexing
        A[AWS S3 Bucket / Local Data] -->|boto3 / Loader| B[src/ingestion.py]
        B --> C[src/preprocessing.py]
        C -->|RecursiveTextSplitter| D[Text Chunks 500 chars]
        D -->|Save Cache| E[(preprocessed_chunks.json)]
        D -->|Embeddings| F[src/vector_store.py]
        F -->|all-MiniLM-L6-v2| G[(Pinecone Vector DB)]
    end

    subgraph Hybrid Retrieval & FlashRank Reranking Pipeline
        H[User Query] --> I[src/hybrid_retriever.py]
        E -->|BM25 Sparse| I
        G -->|Dense Similarity Threshold 0.78| I
        I -->|Top 6 Candidates| J[src/reranker.py]
        J -->|FlashRank Cross-Encoder| K[Top-3 Re-ranked Chunks]
    end

    subgraph LLM Generation & Web Layer
        K --> L[src/rag_pipeline.py]
        M[Groq LLM] <--> L
        L <--> N[app.py / FastAPI Server]
        N <-->|StreamingResponse| O[Interactive UI / Web Browser]
    end

    subgraph Evaluation Suite
        K -.-> P[evaluate_rag.py / src/evaluation.py]
        P -.->|RAGAS Metrics| Q[ragas_evaluation_results.csv]
    end
```

---

## 📂 Project Directory Structure

```text
.
├── Data/                             # Local raw PDF storage directory
│   └── Medical_book.pdf              # Source medical textbook
├── evaluation/                       # RAGAS evaluation suite & benchmarks
│   ├── RAGAS_DATASET_README.md       # Dataset metadata & specifications
│   ├── preprocessed_chunks.json      # Cached chunks for local BM25 index
│   ├── ragas_evaluation_results.csv  # Output metrics CSV report
│   ├── ragas_medical_evaluation_dataset.csv
│   └── ragas_medical_evaluation_dataset.json
├── research/                         # Jupyter notebook experiments & trials
│   └── trials.ipynb
├── src/                              # Core modular Python packages
│   ├── __init__.py
│   ├── evaluation.py                 # RAGAS metric executor with rate limiting & LLM binding
│   ├── exception.py                  # Custom exception handling with line tracing
│   ├── hybrid_retriever.py           # HybridThresholdRetriever (Dense threshold + BM25 Ensemble)
│   ├── ingestion.py                  # AWS S3 downloader & PDF DirectoryLoader
│   ├── logger.py                     # Centralized logging setup
│   ├── preprocessing.py              # Minimal metadata filtering & character chunking
│   ├── prompt.py                     # System prompt templates
│   ├── rag_pipeline.py               # RAG chain construction (ChatGroq + ChatPromptTemplate)
│   ├── reranker.py                   # FlashRank cross-encoder contextual compression retriever
│   └── vector_store.py               # Pinecone index management & HuggingFace embeddings
├── static/                           # UI assets
│   ├── app.png                       # Application screenshot
│   ├── script.js                     # Async JS frontend logic (streaming, markdown, context drawer)
│   └── style.css                     # Modern dark theme styles
├── templates/                        # Frontend HTML templates
│   └── chat.html                     # Main interactive chatbot web interface
├── app.py                            # FastAPI application server & streaming endpoints
├── evaluate_rag.py                   # Orchestration script to run RAGAS benchmark evaluation
├── requirements.txt                  # Python dependencies declaration
├── setup.py                          # Package installation configuration
└── store_index.py                    # Data ingestion & indexing entry point script
```

---

## 💻 Tech Stack

- **Framework**: LangChain `v0.3+`, FastAPI, Uvicorn, Pydantic, Jinja2.
- **LLM Provider**: Groq API (`openai/gpt-oss-120b` / `llama-3.3-70b-versatile`).
- **Vector Database**: Pinecone (`serverless`, cosine distance, 384 dimensions).
- **Embeddings**: HuggingFace `sentence-transformers/all-MiniLM-L6-v2`.
- **Sparse Retrieval**: `rank_bm25` (`BM25Retriever`).
- **Cross-Encoder Reranker**: `FlashRank` (`ms-marco-MiniLM-L-6-v2`).
- **Evaluation**: RAGAS Framework (`faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`).
- **Cloud Storage**: AWS S3 (`boto3`).

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- Pinecone API Key ([pinecone.io](https://www.pinecone.io/))
- Groq API Key ([console.groq.com](https://console.groq.com/))
- AWS S3 Bucket Credentials *(Optional: falls back to local `Data/` folder)*

### 2. Clone & Install Dependencies
```bash
git clone https://github.com/arup04/Medical-Chatbot-Project.git
cd Medical-Chatbot-Project

# Switch to the reranking_improvements branch
git checkout reranking_improvements

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory:
```env
# Required API Keys
PINECONE_API_KEY="your-pinecone-api-key"
GROQ_API_KEY="your-groq-api-key"

# LLM Model Configuration (Optional)
GROQ_MODEL_NAME="openai/gpt-oss-120b"

# AWS S3 Storage Configuration (Optional)
AWS_ACCESS_KEY_ID="your-aws-access-key-id"
AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
AWS_DEFAULT_REGION="us-east-1"
AWS_BUCKET_NAME="your-s3-bucket-name"
AWS_FILE_KEY="Medical_book.pdf"
```

---

## 🚀 Running the Pipeline

### Step 1: Ingestion & Vector Indexing
Download/load the PDF, chunk text, cache chunks locally for BM25, and index vectors in Pinecone:
```bash
python store_index.py
```

### Step 2: Run RAGAS Benchmark Evaluation
Evaluate RAG generation & cross-encoder retrieval quality:
```bash
python evaluate_rag.py
```

### Step 3: Run the Web Application
Launch the FastAPI application:
```bash
python app.py
```
Or run directly via Uvicorn:
```bash
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```
Navigate to **`http://localhost:8080`** in your browser to chat with MediAid AI.

---

## 📊 RAGAS Evaluation Baseline Scores

Evaluation results with Hybrid Search + FlashRank Reranking:

| Metric | Score | Target | Status | Description |
|---|---|---|---|---|
| **Faithfulness** | `0.8932` | > 0.80 | ✅ **Passed** | Factual consistency of response against retrieved context. |
| **Answer Relevancy** | `0.9363` | > 0.80 | ✅ **Passed** | Direct alignment of the response with user query intent. |
| **Context Precision** | `0.7778` | > 0.70 | ✅ **Passed** | Signal-to-noise ratio of top reranked context chunks. |
| **Context Recall** | `1.0000` | > 0.80 | ✅ **Passed** | Complete retrieval of ground-truth reference facts. |

---

## 🔮 Future Roadmap

Upcoming feature branches:
1. **Conversational Memory (`conversational_memory`)**: Stateful multi-turn chat history management, SQLite/PostgreSQL persistence (`src/database.py`), session API routes, and history-aware retrieval chains.

---

## 📜 License & Author

Distributed under the MIT License. See `LICENSE` for details.

- **Author**: Arup Das
- **Repository**: [arup04/Medical-Chatbot-Project](https://github.com/arup04/Medical-Chatbot-Project)