\# 📄 DocuMind – Intelligent PDF Q\&A System (RAG)



DocuMind is a production-style Retrieval-Augmented Generation (RAG) system that enables users to ask questions over PDF documents and receive accurate, context-aware answers using a locally hosted LLM.



\---



\## 🚀 Features



\- 📥 PDF ingestion with metadata (page number, source)

\- 🧹 Advanced preprocessing:

&#x20; - Page-level filtering (removes TOC, noise, irrelevant pages)

&#x20; - Chunk-level filtering

\- 🧩 Multiple chunking strategies:

&#x20; - Token-based splitting

&#x20; - Sentence-transformer-based splitting

&#x20; - Semantic chunking

&#x20; - Recursive character splitting

\- 🔍 Vector similarity search using FAISS

\- 🧠 Context-aware answer generation using local LLM (Mistral via Ollama)

\- ⚡ FastAPI-based API for real-time querying

\- 🏗️ Modular pipeline (fully custom RAG implementation)



\---



\## 🧠 System Architecture



* PDF → Page Filtering → Chunking → Chunk Filtering → Embeddings → FAISS Index

→ Query → Retrieval → Cleaning → Context Building → LLM → Answer





\---



\## 🛠️ Tech Stack



\- Python

\- FastAPI

\- FAISS

\- Sentence Transformers

\- Ollama (Mistral LLM)

\- PyPDF

\- LangChain (used for text splitting strategies)



\---



\## 📦 Installation



\### 1. Clone the repository



```bash

git clone https://github.com/your-username/DocuMind.git

cd DocuMind



\### 2. Install docker, dependencies and set up redis cache



* pip install -r requirements.txt

```bash
docker run -d -p 6379:6379 redis



\### 3. Install and run Ollama



```bash

ollama run mistral



\### 4. Running the API



```bash

uvicorn RAG\_Pipeline:app --reload



\### 5. Open Swagger UI or Postman



\### 6. Test endpoints



\#### a. Upload PDF for cleaning and index creation: **http://127.0.0.1:8000/upload/whole\_path\_to\_pdf/chunking\_ method** (semantic/token/sentence/recursive) [POST]

Example: http://127.0.0.1:8000/upload/C:/Users/abcd/Documents/book.pdf/semantic

Expected result : **{"message" : "PDF uploaded succesfully. Index created"}**



\#### b. Query DocuMind and get the response: **http://127.0.0.1:8000/query/query\_text** [POST]

Example: http://127.0.0.1:8000/query/Is Machine Learning a subset of Artificial Intelligence

Expected result : **{"response" : "response to the users query" , "cached" : true/false}**


\#### c. Evaluate the retrieved chunks: **http://127.0.0.1:8000/evaluate** [GET]

Expected result: Calculated coherence, windowed coherence and readability calculated using textstat





