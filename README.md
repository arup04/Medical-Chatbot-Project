## 🩺 MediBot: AI-Powered Medical RAG Chatbot
`MediBot` is a specialized medical assistant built using a `Retrieval-Augmented Generation (RAG)` architecture. It combines the reasoning capabilities of Groq (LLM) with a Pinecone vector database to provide accurate, context-aware answers based on verified medical documentation.

## 🎥 Demo Video

📺 Watch the demo here:
👉 https://www.youtube.com/watch?v=U0dtvXTgjVk

## 🚀 Features
- Medical document grounded responses using RAG
- Semantic search with Pinecone
- Fast inference using Groq LLM
- Simple web-based chat interface
- Secure API key handling via environment variables


## 🛠️ System Architecture
The chatbot follows a standard RAG pipeline to ensure that answers are grounded in specific data rather than general training knowledge:

`Embeddings`: Uses Hugging Face models to convert medical text into numerical vectors.

`Vector Store`: Vectors are stored and indexed in Pinecone for high-speed similarity searches.

`Retriever`: When a user asks a question, the top 3 most relevant document chunks are retrieved from Pinecone.

`Augmented Generation`: The retrieved context is passed to the ChatGroq model along with the user's query to generate a factual response.



## 🚀 Tech Stack
`Backend`: FastAPI

`LLM`: Groq (ChatGroq)

`Vector DB`: Pinecone

`Orchestration`: LangChain

`Embeddings`: Hugging Face (Sentence Transformers)

`Frontend`: HTML, CSS and JS

## ⚙️ Installation & Setup
1. Clone the Repository
```Bash
git clone https://github.com/arup04/Medical-Chatbot-Project.git
```

```Bash
cd /Medical-Chatbot-Project
```

2. Create and Activate Virtual Environment
```Bash
uv venv
.venv\Scripts\activate
```

3. Set Up Environment Variables
Create a .env file in the root directory and add your credentials:

```Bash
PINECONE_API_KEY=your_pinecone_key
GROQ_API_KEY=your_groq_key
```

3. Install Dependencies

```Bash
uv pip install -r requirements.txt
```

4. Run the Application
```Bash
uvicorn app:app --reload
```

## ⚠️ Medical Disclaimer

This application is for educational purposes only. It uses RAG to provide information based on provided documents. It should not be used for clinical diagnosis or as a substitute for professional medical advice.
