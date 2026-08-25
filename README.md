# 📄 DocuMind — Production-Style RAG System

**🌐 Live Demo:** `https://documind-rag-lab.vercel.app`
**💻 Source Code:** `https://github.com/Saurav-VK/DocuMind`

DocuMind is an end-to-end Retrieval-Augmented Generation (RAG) application for querying PDF documents. It combines hybrid dense + sparse retrieval, Reciprocal Rank Fusion, Cross-Encoder reranking, Redis caching, multiple configurable chunking strategies, persistent document storage, and LLM-based answer generation.

The application includes a React frontend, FastAPI backend, document-level retrieval isolation, automated response evaluation, and a fully deployed cloud architecture using Vercel and Railway.

> **Demo Notice:** DocuMind is a portfolio demonstration and does not currently provide authenticated user accounts. Do not upload confidential, sensitive, or personally identifiable documents.

---

## 🚀 Features

### 📄 Document Processing

* Multi-PDF upload
* Page-level filtering to remove noisy or irrelevant content
* Chunk-level filtering
* Source and page metadata preservation
* Per-document processing and indexing
* Persistent processed-document storage
* Browser/client-specific document isolation

### 🧩 Multiple Chunking Strategies

DocuMind supports four chunking approaches:

* Token-based splitting
* Sentence-Transformer token splitting
* Semantic chunking
* Recursive character splitting

For **Token** and **Recursive** chunking, users can customize:

* Chunk size
* Chunk overlap

Chunking configuration is incorporated into document identification so that different processing configurations can be stored and retrieved independently.

### 🔍 Hybrid Retrieval

DocuMind combines:

* **FAISS** for dense semantic vector retrieval
* **BM25** for sparse lexical retrieval

Results from both retrieval systems are combined using **Reciprocal Rank Fusion (RRF)**.

### 🎯 Cross-Encoder Reranking

Fused retrieval candidates are passed through a Cross-Encoder reranker to improve the relevance of the final context supplied to the LLM.

### ⚡ Redis Caching

Generated responses are cached using Redis to avoid unnecessary repeated retrieval and generation for identical requests.

### 🤖 LLM Answer Generation

Retrieved and reranked chunks are assembled into grounded context and passed to the configured LLM generation layer.

The deployed application uses **Google Gemini**, while the project also supports local LLM experimentation using **Ollama**.

### 📊 Response Evaluation

DocuMind includes an evaluation pipeline covering:

* Coherence
* Window coherence
* Readability
* Faithfulness
* Answer relevancy

DeepEval-based metrics are used for faithfulness and answer relevancy evaluation.

### 🌐 Web Interface

The React frontend provides:

* PDF uploads
* Chunking strategy selection
* Configurable chunk size and overlap
* Document management
* Multi-document selection
* Natural-language querying
* Markdown-formatted answers
* Cache status
* Response evaluation results
* Loading and error states

---

## 🧠 System Architecture

```text
                         ┌─────────────────────┐
                         │     React Client    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     FastAPI API     │
                         └──────────┬──────────┘
                                    │
                              PDF Upload
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Page Filtering   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      Chunking       │
                         │ Token / Sentence /  │
                         │ Semantic / Recursive│
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Chunk Filtering   │
                         └──────────┬──────────┘
                                    │
                         ┌──────────┴──────────┐
                         ▼                     ▼
                  ┌────────────┐        ┌────────────┐
                  │   FAISS    │        │    BM25    │
                  │   Dense    │        │   Sparse   │
                  └─────┬──────┘        └─────┬──────┘
                        │                     │
                        └──────────┬──────────┘
                                   ▼
                         ┌─────────────────────┐
                         │ Reciprocal Rank     │
                         │ Fusion (RRF)        │
                         └──────────┬──────────┘
                                    ▼
                         ┌─────────────────────┐
                         │ Cross-Encoder       │
                         │ Reranking           │
                         └──────────┬──────────┘
                                    ▼
                         ┌─────────────────────┐
                         │   Context Builder   │
                         └──────────┬──────────┘
                                    ▼
                              Redis Cache
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   LLM Generation    │
                         │      Gemini         │
                         └──────────┬──────────┘
                                    ▼
                              Final Answer
                                    │
                         ┌──────────┴──────────┐
                         ▼                     ▼
                    React UI              Evaluation
```

---

## 🛠️ Tech Stack

### Backend

* Python
* FastAPI
* Uvicorn
* PyPDF

### Retrieval & NLP

* FAISS
* Sentence Transformers
* BM25 (`rank-bm25`)
* Cross-Encoder reranking
* Reciprocal Rank Fusion
* LangChain text splitters
* Hugging Face embeddings

### LLM

* Google Gemini
* Ollama for local LLM experimentation

### Evaluation

* DeepEval
* TextStat
* Custom coherence evaluation

### Infrastructure

* Redis
* Docker
* Docker Compose
* Railway

### Frontend

* React
* Vite
* React Markdown
* Vercel

---

## 🌐 Live Deployment

DocuMind is deployed as a multi-service application.

```text
User
  │
  ▼
Vercel
React / Vite Frontend
  │
  │ HTTPS API requests
  ▼
Railway
FastAPI Backend
  │
  ├── Redis
  │
  ├── Persistent Document Storage
  │
  └── Gemini API
```

**Live Application:** `https://documind-rag-lab.vercel.app`

The frontend is hosted on **Vercel**, while the FastAPI backend, Redis service, and persistent application storage are hosted using **Railway**.

---

## 📦 Local Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Saurav-VK/DocuMind.git
cd DocuMind
```

### 2. Install Dependencies

Install the backend requirements:

```bash
pip install -r requirements.txt
```

Install the frontend dependencies from the frontend directory:

```bash
npm install
```

### 3. Start Redis

For local development:

```bash
docker run -d -p 6379:6379 redis
```

Alternatively, use the included Docker Compose configuration.

### 4. Configure Environment Variables

Configure the environment variables required by the backend and frontend before starting the application.

Do **not** commit API keys, Redis credentials, or other secrets to the repository.

For the frontend, configure:

```text
VITE_API_URL=http://localhost:8000
```

### 5. Optional — Local Ollama

For local LLM experimentation:

```bash
ollama run mistral
```

### 6. Start the FastAPI Backend

From the API directory:

```bash
uvicorn RAG_Pipeline:app --reload
```

The local API will be available at:

```text
http://127.0.0.1:8000
```

### 7. Start the React Frontend

From the frontend directory:

```bash
npm run dev
```

Open the Vite development URL displayed in the terminal.

---

## 🔌 Core API Workflow

### Upload Documents

```text
POST /upload/{strategy}
```

Supported strategies:

```text
semantic
token
sentence
recursive
```

The request accepts PDF files using `multipart/form-data`.

Token and recursive strategies additionally support configurable chunk size and chunk overlap values.

The API processes each document, generates chunks, creates FAISS and BM25 indexes, and stores the resulting artifacts for subsequent retrieval.

### List Documents

```text
GET /documents
```

Returns documents associated with the requesting browser/client identifier.

### Delete Document

```text
DELETE /documents/{document_hash}
```

Deletes the selected processed document belonging to that client.

### Query Documents

```text
POST /query
```

The request specifies:

* User query
* Selected document hashes

DocuMind performs hybrid retrieval, RRF fusion, Cross-Encoder reranking, context construction, cache lookup, and LLM generation before returning the answer.

Example response:

```json
{
  "response": "Generated answer grounded in the selected documents.",
  "cached": false
}
```

### Evaluate Response

```text
POST /evaluate
```

Evaluates the generated response using metrics including:

* Coherence
* Window coherence
* Readability
* Faithfulness
* Answer relevancy

---

## 🐳 Docker

Build the application image:

```bash
docker build -t documind .
```

Run the complete local stack using Docker Compose:

```bash
docker compose up -d --build
```

To stop the stack:

```bash
docker compose down
```

Docker Compose provides the local multi-container environment required by the API and Redis.

---

## 📈 Retrieval Pipeline

1. User uploads one or more PDF documents.
2. Each PDF is validated and processed.
3. Invalid/noisy pages are filtered.
4. Text is split using the selected chunking strategy.
5. Invalid chunks are removed.
6. Dense embeddings are generated.
7. Embeddings are indexed using FAISS.
8. A sparse BM25 index is created.
9. Processed document artifacts are persisted.
10. User selects one or more documents and submits a query.
11. FAISS performs dense semantic retrieval.
12. BM25 performs sparse lexical retrieval.
13. Reciprocal Rank Fusion combines both rankings.
14. Cross-Encoder reranking refines the candidate set.
15. Top-ranked chunks are cleaned and assembled into LLM context.
16. Redis is checked for a cached response.
17. The LLM generates a grounded answer when required.
18. The response is returned to the React frontend.
19. Users can optionally evaluate the generated response.

---

## 🔐 Data & Privacy

DocuMind currently uses a browser-generated client identifier to associate uploaded documents with a particular browser.

The application does **not** currently provide authenticated user accounts.

As a result:

* Users should not upload confidential or sensitive documents.
* Clearing browser storage may remove access to previously uploaded documents.
* Documents are not automatically accessible across browsers or devices.
* The public deployment is intended as a portfolio demonstration.

---

## 🎯 Future Improvements

* Authentication and user accounts
* Cross-device document recovery
* Streaming LLM responses
* Expanded retrieval evaluation and observability
* Production-grade rate limiting
* More advanced document formats and ingestion pipelines

---

## 👨‍💻 Author

**Saurav VK**

Built as an end-to-end exploration of production-style Retrieval-Augmented Generation systems, hybrid information retrieval, reranking, evaluation, caching, containerization, persistent storage, and cloud deployment.

**🌐 Live Demo:** `YOUR_VERCEL_LINK_HERE`
**💻 GitHub:** `https://github.com/Saurav-VK/DocuMind`
