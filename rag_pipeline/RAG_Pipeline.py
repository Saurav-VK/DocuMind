#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pdf_loader import *
from page_filter import *
from chunking_strategies import *
from text_chunker import *
from faiss_store import *
from retrieval import *
from clean_for_llm import *
from chunk_filter import *
from generation import *
from evaluation import *
from Create_BM25_Index import *
from BM25_retreival import *
from reciprocal_ranking_fusion import *
from ReRanker import *
from evaluate_RAG import *
from document_hasher import *
from storage_utils import *
from document_processor import *  
from multi_pdf_retrieval import *
from logger import logger
import time
import redis
import shutil
import hashlib
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException

# In[4]:


from fastapi import FastAPI , UploadFile , File , Header , Form
from typing import List

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR , exist_ok = True)

STORAGE_DIR = "storage"
os.makedirs(STORAGE_DIR , exist_ok = True)

'''for file in os.listdir(UPLOAD_DIR):
    os.remove(os.path.join(UPLOAD_DIR, file))'''

app = FastAPI()

FRONTEND_URL = os.getenv("FRONTEND_URL" , "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("DocuMind API initialized")

def rate_limiter(client_id , action , limit , window_seconds):

    key = f"rate_limit:{action}:{client_id}"

    current = r.incr(key)

    if current == 1:
        r.expire(key , window_seconds)

    if current > limit:
        raise HTTPException(status_code = 429 , detail = "Rate limit reached for {action}. Please try again later.")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "DocuMind API"
    }


@app.post("/upload/{strategy}")
def upload_and_store(strategy : str , files : List[UploadFile] = File(...) , chunk_size: int | None = Form(None) , chunk_overlap: int | None = Form(None), x_client_id: str = Header(...)):

    MAX_FILES = 5
    MAX_PAGES = 30

    if strategy in ["token" , "recursive"]:

        if chunk_size is None:
            chunk_size = 200 if strategy == "token" else 100

        if chunk_overlap is None:
            chunk_overlap = 40

        if chunk_size < 50 or chunk_size > 500:
            raise HTTPException(status_code = 400 , detail = "Chunk size must be between 50 and 500")

        if chunk_size < 0 or chunk_overlap >= chunk_size:
            raise HTTPException(status_code = 400 , detail = "Chunk overlap must be gretaer than or equal to 0 and smaller than the chunk size")

    else:
        chunk_size = None
        chunk_overlap = None

    logger.info("Uplaod request | client = %s" , x_client_id)
    logger.info("Upload started | files = %d | strategy = %s" , len(files) , strategy)

    if len(files) > MAX_FILES:
        logger.warning("Upload rejected | client id = %s | files uploaded = %d | max files = %d" , x_client_id , len(files) , MAX_FILES)

        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_FILES} PDFs allowed per upload"
        )

    saved_file_paths = []
    total_pages = 0

    for file in files:

        if not file.filename.lower().endswith(".pdf"):

            logger.warning("Upload rejected | invalid file type | file == %s" , file.filename)

            return {"error" : f"Invalid file type detected: {file.filename}. Please upload pdfs only"}

        logger.info("Receiving uploaded document | file = %s" , file.filename)

        file_path = os.path.join(UPLOAD_DIR , file.filename)

        with open(file_path , "wb") as f:
            f.write(file.file.read())

        saved_file_paths.append(file_path)

        pdf_reader = PdfReader(file_path)
        total_pages += len(pdf_reader.pages)

        logger.info("Page count checked | file = %s | pages = %d | total pages = %d", file.filename , len(pdf_reader.pages) , total_pages)

        if total_pages > MAX_PAGES:

            logger.warning("Upload rejected | client id = %s | total pages uploaded = %d | page limit = %d" , x_client_id , total_pages , MAX_PAGES)

            raise HTTPException(
                status_code=400,
                detail=f"Maximum {MAX_PAGES} total pages allowed per upload"
            )

    for file_path in saved_file_paths:

        file_name = os.path.basename(file_path)

        logger.info("Processing uplaoded document | file = %s", file_name)

        chunks , faiss_index , bm25_index = process_documents(file_path , strategy , STORAGE_DIR , x_client_id , chunk_size , chunk_overlap)

        logger.info("Document ready | file = %s | chunks = %d" , file_name , len(chunks))

    logger.info("Upload completed | files = %s | total pages = %d" , len(files) , total_pages)

    return {"message" : "PDFs uploaded and processed succesfully."}        

        

def normalize_query(query):
    return query.lower().strip()

def generate_cache_key(client_id , document_hashes , query):

    normalized_query = normalize_query(query)

    sorted_doc_hashes = sorted(document_hashes)

    raw_key = (client_id + ":" + ":".join(sorted_doc_hashes) + ":" + normalized_query)

    cache_key = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    return cache_key


REDIS_URL = os.getenv("REDIS_URL")

if REDIS_URL:
    r = redis.from_url(
        REDIS_URL,
        decode_responses=False
    )
else:
    r = redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=0
    )

class QueryRequest(BaseModel):
    query : str
    documents : List[str]

class EvaluationRequest(BaseModel):
    query: str
    answer: str
    documents: List[str]

@app.post("/query")
def query_response(request : QueryRequest , x_client_id : str = Header(...)):

    start_time = time.perf_counter()

    query = request.query
    document_hashes = request.documents

    logger.info("Query received")

    app.state.query = query

    normalized_query = normalize_query(query)

    cache_key = generate_cache_key(
    x_client_id,
    document_hashes,
    query
    )

    cached = r.get(cache_key)

    if cached:

        elapsed = time.perf_counter() - start_time

        logger.info(
        "Cache hit | time=%.3fs",
        elapsed
        )

        return {
               "response" : cached.decode() ,
               "cached" : True
               }

    logger.info("Cache miss")
    
    all_chunks = []
    
    all_faiss_indexes = []

    all_bm25_indexes = []

    for document_hash in document_hashes:

        document_dir = os.path.join(STORAGE_DIR , x_client_id , document_hash)

        if not os.path.exists(document_dir):
            return {"error" : f"Document not found: {document_hash}"}

        chunks = load_chunks(document_dir)
        faiss_index = load_faiss_index(document_dir)
        bm25_index = load_bm25_index(document_dir)

        all_chunks.append(chunks)
        all_faiss_indexes.append(faiss_index)
        all_bm25_indexes.append(bm25_index)


    all_faiss_results , all_bm25_results = retrieve_from_multiple_pdfs(query , all_chunks , all_faiss_indexes , all_bm25_indexes , k = 5)

    logger.info(
    "Retrieval completed | faiss_results=%d | bm25_results=%d",
    len(all_faiss_results),
    len(all_bm25_results)
    )

    rrf_chunks = reciprocal_rank_fusion(all_faiss_results , all_bm25_results)

    logger.info(
    "RRF completed | candidates=%d",
    len(rrf_chunks)
    )

    results = reranker_function(query , rrf_chunks)

    logger.info(
    "Cross-encoder reranking completed | results=%d",
    len(results)
    )

    app.state.retrieved_chunks = results

    cleaned_results = [clean_for_llm(result) for result in results]

    print(cleaned_results)

    logger.info("LLM generation started")

    try:

        response = answer_query(query , cleaned_results)

    except Exception:
   
        logger.exception("LLM Generation failed")
        raise

    logger.info("LLM generation completed")

    app.state.response = response

    r.setex(cache_key , 300 , response)

    elapsed = time.perf_counter() - start_time

    logger.info(
        "Query completed | cached=False | time=%.3fs",
        elapsed
    )

    return {
            "response" : response ,
            "cached" : False
           }


@app.post("/evaluate")
def evaluate_response(request : EvaluationRequest ,  x_client_id : str = Header(...)):

    logger.info("Evaluation started | client_id = %s" , x_client_id)

    query = request.query
    answer = request.answer
    document_hashes = request.documents

    all_chunks = []
    all_faiss_indexes = []
    all_bm25_indexes = []

    for document_hash in document_hashes:
        document_dir = os.path.join(STORAGE_DIR , x_client_id , document_hash)

        if not os.path.exists(document_dir):
            return {"error" : f"Document not found : {document_hash}"}

        chunks = load_chunks(document_dir)
        faiss_index = load_faiss_index(document_dir)
        bm25_index = load_bm25_index(document_dir)

        all_chunks.append(chunks)
        all_faiss_indexes.append(faiss_index)
        all_bm25_indexes.append(bm25_index)

    all_faiss_results, all_bm25_results = retrieve_from_multiple_pdfs(
        query,
        all_chunks,
        all_faiss_indexes,
        all_bm25_indexes,
        k=5
    )

    rrf_chunks = reciprocal_rank_fusion(
        all_faiss_results,
        all_bm25_results
    )

    retrieved_chunks = reranker_function(
        query,
        rrf_chunks
    )

    chunk_content = [
        chunk["text"]
        for chunk in retrieved_chunks
    ]   

    coherence = evaluate_coherence(
        chunk_content
    )

    logger.info(
        "Coherence metric completed"
    )

    window_coherence = evaluate_window_coherence(
        chunk_content
    )

    logger.info(
        "Window coherence metric completed"
    )

    readability = evaluate_readability(
        chunk_content
    )

    logger.info(
        "Readability metric completed"
    )

    logger.info(
        "DeepEval started"
    )

    metrics = evaluate_RAG(
        query,
        chunk_content,
        answer
    )

    logger.info(
        "DeepEval completed"
    )

    logger.info(
        "Evaluation completed | client_id=%s",
        x_client_id
    )

    return {
           "Coherence" : coherence , 
           "Window coherence for slow context drifting" : window_coherence ,
           "Readability score" : readability ,
           "Deep Eval Metrics" : metrics
           }


@app.get("/documents")
def get_documents(x_client_id : str = Header(...)):

    client_dir = os.path.join(STORAGE_DIR , x_client_id)

    logger.info(
        "Documents request | client_id=%s | client_dir=%s",
        x_client_id,
        client_dir
               )

    if not os.path.exists(client_dir):
        logger.warning("Client directory does not exist")
        return []

    logger.info(
        "Client directory contents: %s",
        os.listdir(client_dir)
    )

    documents = []

    for document_hash in os.listdir(client_dir):

        document_dir = os.path.join(client_dir , document_hash)

        logger.info(
            "Checking document directory: %s",
            document_dir
                   )

        if not os.path.isdir(document_dir):
            continue

        metadata_file = os.path.join(document_dir , "metadata.json")

        logger.info(
            "Metadata exists: %s",
            os.path.exists(metadata_file)
                   )

        if not os.path.exists(metadata_file):
            continue

        metadata = load_metadata(document_dir)

        documents.append(metadata)

    return documents

@app.delete("/documents/{document_hash}")
def delete_document(document_hash : str , x_client_id : str = Header(...)):

    document_dir = os.path.join(STORAGE_DIR , x_client_id  , document_hash)

    if not os.path.exists(document_dir):

        logger.warning("Delete failed | client_id = %s | document_hash = %s | document not found" , x_client_id , document_hash)

        return {"error" : "Document not found"}

    shutil.rmtree(document_dir)

    logger.info("Document deleted | client_id = %s | document_hash = %s" , x_client_id , document_hash)

    return {"message" : "Document deleted successfully"}