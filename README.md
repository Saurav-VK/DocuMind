# 📄 DocuMind – Intelligent PDF Q&A System (RAG)

DocuMind is a production-style Retrieval-Augmented Generation (RAG) system that combines hybrid retrieval (FAISS + BM25), Reciprocal Rank Fusion (RRF), Cross-Encoder reranking, Redis caching, and a locally hosted LLM to provide accurate and context-aware answers from PDF documents.

---

## 🚀 Features

* 📥 PDF ingestion with metadata (page number, source)

* 🧹 Advanced preprocessing:

  * Page-level filtering (removes TOC, noise, irrelevant pages)
  * Chunk-level filtering

* 🧩 Multiple chunking strategies:

  * Token-based splitting
  * Sentence-transformer-based splitting
  * Semantic chunking
  * Recursive character splitting

* 🔍 Vector similarity search using FAISS

* 🔎 Hybrid retrieval using FAISS (dense retrieval) + BM25 (sparse retrieval)

* 🔀 Reciprocal Rank Fusion (RRF) for combining retrieval results

* 🎯 Cross-Encoder reranking for improved retrieval relevance

* ⚡ Redis-based response caching

* 🧠 Context-aware answer generation using local LLM (Mistral via Ollama)

* 📂 Multi-file upload support via API

* 🐳 Dockerized deployment

* 🐳 Docker Compose support for multi-container orchestration

* 🏗️ Modular pipeline (fully custom RAG implementation)

---

## 🧠 System Architecture

PDF → Page Filtering → Chunking → Chunk Filtering

→ Embeddings → FAISS Index

→ BM25 Index

→ Query

→ Dense Retrieval + Sparse Retrieval

→ Reciprocal Rank Fusion (RRF)

→ Cross-Encoder Reranking

→ Context Building

→ Redis Cache Check

→ LLM (Mistral)

→ Answer

---

## 🛠️ Tech Stack

* Python
* FastAPI
* FAISS
* Sentence Transformers
* BM25 (rank-bm25)
* Cross Encoder (Sentence Transformers)
* Redis
* Ollama (Mistral LLM)
* PyPDF
* LangChain (used for text splitting strategies)
* Docker
* Docker Compose

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/DocuMind.git

cd DocuMind
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Redis

```bash
docker run -d -p 6379:6379 redis
```

### 4. Install and run Ollama

```bash
ollama run mistral
```

### 5. Run the API

```bash
uvicorn RAG_Pipeline:app --reload
```

### 6. Open Swagger UI or Postman

### 7. Test Endpoints

#### a. Upload PDF(s) for cleaning, chunking, indexing and retrieval preparation

**POST**

```text
http://127.0.0.1:8000/upload/method
```

Choose one of:

```text
semantic
token
sentence
recursive
```

Example:

```text
http://127.0.0.1:8000/upload/semantic
```

Testing in Postman:

* Select Body → form-data
* Key = files
* Type = File
* Select one or more PDF files from your device

Expected Result:

```json
{
  "message": "PDF uploaded successfully. Index created"
}
```

---

#### b. Query DocuMind and get a response

**POST**

```text
http://127.0.0.1:8000/query/query_text
```

Example:

```text
http://127.0.0.1:8000/query/Is Machine Learning a subset of Artificial Intelligence
```

Expected Result:

```json
{
  "response": "response to the users query",
  "cached": true
}
```

or

```json
{
  "response": "response to the users query",
  "cached": false
}
```

---

#### c. Evaluate Retrieved Chunks

**GET**

```text
http://127.0.0.1:8000/evaluate
```

Expected Result:

* Coherence Score
* Windowed Coherence Score
* Readability Score

Calculated using TextStat.

---

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t documind .
```

### Create Network

```bash
docker network create documind-network
```

### Run Redis

```bash
docker run -d --name redis-server --network documind-network redis
```

### Run API

```bash
docker run -d \
--name documind-api \
--network documind-network \
-p 8000:8000 \
documind
```

---

## 🐳 Docker Compose (Recommended)

Run the complete application stack:

```bash
docker compose up -d --build
```

This automatically:

* Builds the API image
* Creates the Docker network
* Starts Redis
* Starts FastAPI
* Connects all services together

To stop all services:

```bash
docker compose down
```

---

## 📈 Retrieval Pipeline

1. User uploads PDF documents
2. Documents are cleaned and filtered
3. Chunks are generated using the selected chunking strategy
4. Dense embeddings are created and stored in FAISS
5. Sparse BM25 indexes are created
6. User submits a query
7. FAISS and BM25 retrieve relevant chunks independently
8. Reciprocal Rank Fusion (RRF) combines both retrieval results
9. Cross-Encoder reranks the fused results
10. Top-ranked chunks are used as context
11. Redis checks for cached responses
12. Mistral generates the final answer
13. Response is returned to the user

---

## 🎯 Future Improvements

* User-specific knowledge bases
* Persistent vector database support
* Frontend dashboard
* Authentication and user management
* Cloud deployment (AWS/Azure)
* Streaming LLM responses
* Evaluation dashboard for retrieval performance
