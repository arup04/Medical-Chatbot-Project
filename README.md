# 🩺 MediAid AI — Clinical Hybrid RAG Assistant

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-v0.3+-green.svg)](https://python.langchain.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![Pinecone](https://img.shields.io/badge/Pinecone-Serverless-blueviolet.svg)](https://www.pinecone.io/)
[![Sarvam AI](https://img.shields.io/badge/Sarvam_AI-sarvam--105b-orange.svg)](https://www.sarvam.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An end-to-end **Clinical Decision Support & Patient Education AI Assistant** built on a multi-stage Retrieval-Augmented Generation (RAG) architecture. Grounded strictly in authoritative medical literature (*The Gale Encyclopedia of Medicine*), MediAid AI integrates **Pinecone dense vector search**, **local BM25 sparse keyword retrieval**, **Sarvam AI (`sarvam-105b`)**, **multi-layered clinical guardrails**, **thread-safe persistent SQLite multi-turn conversational memory**, and continuous quality evaluation via the **RAGAS framework**.

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [Project Directory Structure](#-project-directory-structure)
- [Deep-Dive: Core Subsystems](#-deep-dive-core-subsystems)
  - [1. Data Ingestion & Hybrid Retrieval](#1-data-ingestion--hybrid-retrieval)
  - [2. Multi-Turn Conversational Memory](#2-multi-turn-conversational-memory)
  - [3. Clinical Guardrails Suite](#3-clinical-guardrails-suite)
  - [4. Real-Time Token & Context Streaming](#4-real-time-token--context-streaming)
  - [5. Clinical Web UI & Citations Explorer](#5-clinical-web-ui--citations-explorer)
- [Tech Stack](#-tech-stack)
- [Environment Variables](#-environment-variables)
- [Installation & Setup](#-installation--setup)
- [Running the Application](#-running-the-application)
- [Running with Docker](#-running-with-docker)
- [API Endpoints Reference](#-api-endpoints-reference)
- [RAGAS Evaluation Benchmarks](#-ragas-evaluation-benchmarks)
- [License & Author](#-license--author)

---

## 🌟 Key Features

- **🔀 Hybrid Search (Dense + Sparse)**: Combines dense semantic embeddings (`sentence-transformers/all-MiniLM-L6-v2`) with sparse keyword matching (`BM25Retriever`) via an `EnsembleRetriever` with 50/50 reciprocal rank weighting.
- **🇮🇳 Sarvam AI Generation**: Powered by Sarvam AI (`sarvam-105b` via `langchain-sarvam`) for factual, low-latency, and hallucination-resistant clinical generation.
- **🧠 Multi-Turn Conversational Memory**:
  - Persistent **SQLite database storage** (`src/chat_history.py`) for thread isolation and multi-turn state preservation across server restarts.
  - **History-Aware Retriever** (`create_history_aware_retriever`) that automatically reformulates follow-up queries using prior chat context (e.g. *"What are its symptoms?"* -> *"What are the symptoms of Type 2 Diabetes?"*).
- **🛡️ Multi-Tiered Clinical Guardrails**:
  - **Input Guardrails** (`Guardrails/input/`): Real-time triage for emergency red-flag symptoms, exact drug dosage query rejection, prompt injection defense, and automated PII de-identification.
  - **Output Guardrails** (`Guardrails/output/`): Automated prescription detection, lethal remedy safety checks, and dynamic mandatory medical disclaimers.
- **🎯 Dynamic Out-of-Domain Filtering**: Custom `HybridThresholdRetriever` enforcing a Pinecone similarity score threshold (`0.78`) to reject non-medical and out-of-domain queries.
- **📡 Real-Time Token & Context Streaming**: FastAPI backend using asynchronous `StreamingResponse` to broadcast live token streams (`[ANSWER]`) alongside structured retrieval metadata (`[CONTEXT]`).
- **🖥️ Clinical Web UI & Citations Drawer**:
  - 3-column responsive layout with dark and light theme switching.
  - Clean consolidated inline citation badges (e.g. `📖 The Gale Encyclopedia of Medicine · 7 Verified Passages`).
  - Interactive **Retrieved Context** panel displaying passage excerpts, similarity match percentages, and click-to-focus inspection.
  - Voice input (Speech-to-Text via Web Speech API) and audio read-aloud playback (Text-to-Speech via SpeechSynthesis).
  - Multi-session consultation switcher and text log export.

---

## 📂 Project Directory Structure

```text
Medical-Chatbot-Project/
├── Data/                             # Local medical textbook storage
│   └── Medical_book.pdf              # The Gale Encyclopedia of Medicine (Source Reference)
├── Evaluation/                       # RAGAS evaluation suite & performance benchmarks
│   ├── final_rag_application_audit_sarvam.csv
│   ├── preprocessed_chunks.json      # Cached chunks for local BM25 index
│   ├── rag_evaluation_sarvam.ipynb   # Resumable Sarvam AI benchmark notebook
│   ├── rag_stage_comparison_sarvam.csv
│   ├── ragas_medical_evaluation_dataset.csv
│   └── ragas_medical_evaluation_dataset.json
├── Guardrails/                       # Multi-tier clinical safety suite
│   ├── input/                        # Input guardrail filters
│   │   ├── __init__.py
│   │   ├── dosage.py                 # Exact dosage query rejection
│   │   ├── emergency.py              # Emergency symptom triage detection
│   │   ├── injection.py              # Prompt injection & jailbreak defense
│   │   ├── models.py                 # Pydantic models for input validation
│   │   ├── pii.py                    # Automated PII detection & redaction
│   │   └── pipeline.py               # Composite input guardrails runner
│   ├── output/                       # Output safety verification
│   │   ├── __init__.py
│   │   ├── disclaimer.py             # Mandatory dynamic disclaimer injection
│   │   ├── faithfulness.py           # Context-grounded consistency check
│   │   ├── models.py                 # Pydantic models for output safety
│   │   ├── pipeline.py               # Composite output guardrails runner
│   │   └── safety.py                 # Unverified prescription & harm auditor
│   └── README.md                     # Guardrails architecture & documentation
├── research/                         # Prototyping & exploratory analysis
│   └── trials.ipynb
├── src/                              # Core Python packages & modular pipeline
│   ├── __init__.py
│   ├── chat_history.py               # SQLite persistent multi-turn conversation memory
│   ├── exception.py                  # Custom exception handling with stack-trace logging
│   ├── hybrid_retriever.py           # HybridThresholdRetriever (BM25 + Dense threshold)
│   ├── ingestion.py                  # AWS S3 downloader & PDF DirectoryLoader
│   ├── logger.py                     # Centralized logging configuration
│   ├── preprocessing.py              # Metadata extraction & text chunking
│   ├── prompt.py                     # Contextualization & grounded QA prompt templates
│   ├── rag_pipeline.py               # History-aware retrieval chain with Sarvam AI
│   └── vector_store.py               # Pinecone index management & Hugging Face embeddings
├── static/                           # Frontend assets
│   ├── app.png                       # Chatbot avatar asset
│   ├── script.js                     # Async streaming, voice I/O, citations logic
│   └── style.css                     # Responsive clinical SaaS styling (Dark/Light themes)
├── templates/                        # Frontend HTML templates
│   └── chat.html                     # Clinical chatbot interface
├── .dockerignore                     # Docker build exclusion rules
├── .env                              # Environment variables (API Keys, Configs)
├── .gitignore                        # Git ignore patterns (*.db, *.sqlite, checkpoints)
├── app.py                            # FastAPI application server & streaming endpoints
├── Dockerfile                        # Containerized build & deployment specification
├── requirements.txt                  # Python dependencies declaration
├── setup.py                          # Package installation configuration
├── store_index.py                    # Ingestion & vector indexing CLI script
└── README.md                         # Project documentation
```

---

## 🔬 Deep-Dive: Core Subsystems

### 1. Data Ingestion & Hybrid Retrieval
- **PDF Extraction**: Ingests textbook PDFs dynamically from AWS S3 storage buckets (via `boto3`) with automatic fallback to local `Data/Medical_book.pdf`.
- **Text Chunking**: Uses `RecursiveCharacterTextSplitter` with `chunk_size=500` and `chunk_overlap=20`. Preprocessed chunks are cached in `Evaluation/preprocessed_chunks.json` for instant BM25 sparse index initialization.
- **Dense Embeddings**: Generates 384-dimensional dense vectors using `sentence-transformers/all-MiniLM-L6-v2` and persists them to a serverless Pinecone index.
- **Hybrid Threshold Retriever**: `HybridThresholdRetriever` combines the sparse `BM25Retriever` with Pinecone dense similarity search via `EnsembleRetriever(weights=[0.5, 0.5])`. If the top Pinecone cosine similarity score is below `0.78`, the query is flagged as out-of-domain.

### 2. Multi-Turn Conversational Memory
- **Persistent SQLite Storage (`src/chat_history.py`)**: Uses a thread-safe local SQLite database with WAL mode to record every user prompt and bot response under a unique `session_id`.
- **History-Aware Retrieval Chain (`src/rag_pipeline.py`)**:
  1. LangChain's `create_history_aware_retriever` passes the chat history and latest user query to Sarvam AI with a contextualization prompt.
  2. The LLM reformulates pronouns and conversational references into a standalone query.
  3. The standalone query is sent to `HybridThresholdRetriever`, ensuring follow-up queries retrieve the correct context passages.

### 3. Clinical Guardrails Suite
- **Input Guardrails (`Guardrails/input/`)**:
  - `emergency.py`: Regex and keyword heuristics scan for 30+ critical red-flag terms (e.g. *chest pain, shortness of breath, slurred speech, suicidal ideation*). If detected, returns immediate emergency triage instructions (911/112/999).
  - `dosage.py`: Intercepts prompts seeking exact drug dosages or medication administration amounts.
  - `injection.py`: Defends against prompt injection, roleplay attacks, and system prompt exfiltration.
  - `pii.py`: Identifies and redacts Social Security numbers, phone numbers, email addresses, and names using regex and contextual entity masks before LLM processing.
- **Output Guardrails (`Guardrails/output/`)**:
  - `safety.py`: Audits generated responses to ensure the model does not issue prescription orders, recommend lethal dosages, or provide unmonitored home treatment advice.
  - `disclaimer.py`: Appends a mandatory standardized medical disclaimer to responses discussing clinical diagnoses or treatments.

### 4. Real-Time Token & Context Streaming
- **FastAPI Streaming Protocol**: The `/get` endpoint streams chunks using Server-Sent Events (SSE) formatting:
  - `[CONTEXT] <json_array>`: Broadcasts retrieved textbook passage text, source paths, and metadata.
  - `[ANSWER] <token>`: Live streaming text tokens from the Sarvam AI generator.
  - `[ERROR] <message>`: Signal for caught exceptions.
  - `[DONE]`: Completion signal.

### 5. Clinical Web UI & Citations Explorer
- **Adaptive Layout**: 3-column architecture (Sidebar, Main Viewport, Retrieved Context drawer) with strict `height: 100dvh` viewport boundaries to prevent input container clipping.
- **Consolidated Citation Pills**: Aggregates passages from identical sources into clean badges (e.g. `📖 The Gale Encyclopedia of Medicine · 7 Verified Passages`).
- **Interactive Context Drawer**: Displays individual source passages with real-time relevance match bars. Clicking a citation pill focuses and highlights the corresponding excerpt in the side panel.
- **Voice I/O**: Integrated Speech-to-Text (microphone button) and Text-to-Speech (read-aloud button).

---

## 💻 Tech Stack

| Component | Technology | Description |
|---|---|---|
| **LLM Generator** | [Sarvam AI](https://www.sarvam.ai/) (`sarvam-105b`) | High-accuracy clinical text generation |
| **Orchestration** | [LangChain](https://python.langchain.com/) `v0.3+` | RAG chains, history-aware retrievers, document combiners |
| **Dense Vector DB** | [Pinecone Serverless](https://www.pinecone.io/) | Dense vector indexing (384-dim, Cosine Distance) |
| **Embeddings** | Hugging Face `all-MiniLM-L6-v2` | Dense sentence embedding model |
| **Sparse Retrieval** | `rank_bm25` | Sparse keyword index for hybrid search |
| **Memory Store** | SQLite | Thread-safe multi-turn chat history persistence |
| **Web Server** | FastAPI & Uvicorn | Asynchronous token & context streaming server |
| **Frontend** | Vanilla HTML5 / CSS3 / JavaScript | Responsive clinical interface (Dark/Light modes) |
| **Evaluation** | [RAGAS](https://github.com/explodinggradients/ragas) | Faithfulness, Answer Relevancy, Context Precision/Recall |
| **Cloud Storage** | AWS S3 (`boto3`) | Cloud PDF document storage and synchronization |

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory:

```env
# ==============================================================================
# MediAid AI Configuration
# ==============================================================================

# Required: Vector Database & LLM Provider API Keys
PINECONE_API_KEY="your-pinecone-api-key"
SARVAM_API_KEY="your-sarvam-api-key"

# Optional: Sarvam Model Name (Defaults to sarvam-105b)
SARVAM_MODEL_NAME="sarvam-105b"

# Optional: AWS S3 Storage (Falls back to local Data/ directory if omitted)
AWS_ACCESS_KEY_ID="your-aws-access-key-id"
AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
AWS_DEFAULT_REGION="us-east-1"
AWS_BUCKET_NAME="your-s3-bucket-name"
AWS_FILE_KEY="Medical_book.pdf"
```

---

## 📦 Installation & Setup

### 1. Prerequisites
- Python 3.10 or higher
- Git
- Active Pinecone and Sarvam AI accounts

### 2. Clone the Repository
```bash
git clone https://github.com/arup04/Medical-Chatbot-Project.git
cd Medical-Chatbot-Project
```

### 3. Create & Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🚀 Running the Application

### Step 1: Ingestion & Vector Indexing
Download/load the PDF, split chunks, cache BM25 sparse index, and push dense embeddings to Pinecone:
```bash
python store_index.py
```

### Step 2: Launch the FastAPI Web Server
Start the development server with hot-reloading:
```bash
python app.py
```
Or start directly with Uvicorn:
```bash
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

### Step 3: Open in Browser
Navigate to **`http://localhost:8080`** to interact with MediAid AI.

---

## 🐳 Running with Docker

You can containerize and run the complete application using Docker:

### 1. Build the Docker Image
```bash
docker build -t mediaid-ai:latest .
```

### 2. Run the Container
```bash
docker run -d \
  --name mediaid-app \
  -p 8080:8080 \
  --env-file .env \
  mediaid-ai:latest
```

The container includes built-in healthchecks to verify server availability. Access the UI at **`http://localhost:8080`**.

## 🌐 API Endpoints Reference

| Method | Endpoint | Parameters | Description |
|---|---|---|---|
| `GET` | `/` | None | Renders the primary clinical chatbot web application. |
| `POST` | `/get` | `msg` (string, Form), `session_id` (string, Form) | Streams LLM response tokens and retrieved context metadata via SSE. |
| `POST` | `/clear_history` | `session_id` (string, Form) | Clears conversation history for the specified session in SQLite. |

---

## 📊 RAGAS Evaluation Benchmarks

The pipeline was benchmarked using the **RAGAS framework** across multiple iterations (Dense-only, Hybrid BM25+Dense, and Hybrid + FlashRank Reranking):

| Metric | Score | Target Threshold | Benchmark Status | Definition |
|---|---|---|---|---|
| **Faithfulness** | **`0.8932`** | > 0.80 | ✅ **Passed** | Measures factual consistency of generated answers against retrieved context. |
| **Answer Relevancy** | **`0.9363`** | > 0.80 | ✅ **Passed** | Evaluates how directly the answer addresses the user's initial question. |
| **Context Precision** | **`0.7778`** | > 0.70 | ✅ **Passed** | Evaluates the signal-to-noise ratio in top retrieved context chunks. |
| **Context Recall** | **`1.0000`** | > 0.80 | ✅ **Passed** | Measures whether all ground-truth reference facts were retrieved. |

*Evaluation scripts, baseline datasets, and comparison audit CSVs are located in [`Evaluation/`](./Evaluation/).*

---

## 📜 License & Author

Distributed under the **MIT License**. See `LICENSE` for details.

- **Author**: [Arup Das](https://github.com/arup04)
- **Repository**: [arup04/Medical-Chatbot-Project](https://github.com/arup04/Medical-Chatbot-Project)