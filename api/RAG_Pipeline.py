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

# In[4]:


from fastapi import FastAPI , UploadFile , File
from typing import List

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR , exist_ok = True)

STORAGE_DIR = "storage"
os.makedirs(STORAGE_DIR , exist_ok = True)

'''for file in os.listdir(UPLOAD_DIR):
    os.remove(os.path.join(UPLOAD_DIR, file))'''

app = FastAPI()

logger.info("DocuMind API initialized")

@app.post("/upload/{strategy}")
def upload_and_store(strategy : str , files : List[UploadFile] = File(...)):

    logger.info(
    "Upload started | files=%d | strategy=%s",
    len(files),
    strategy
    )

    all_chunks = []
    all_faiss_indexes = []
    all_bm25_indexes = []

    for file in files:

        logger.info(
        "Processing uploaded document | file=%s",
        file.filename
        )

        file_path = os.path.join(UPLOAD_DIR , file.filename)

        with open(file_path , "wb") as f:
            f.write(file.file.read())

        chunks , faiss_index , bm25_index = process_documents(file_path , strategy , STORAGE_DIR)

        logger.info(
        "Document ready | file=%s | chunks=%d",
        file.filename,
        len(chunks)
        )

        all_chunks.append(chunks)
        all_faiss_indexes.append(faiss_index)
        all_bm25_indexes.append(bm25_index)

    app.state.chunks = all_chunks
    app.state.faiss_indexes = all_faiss_indexes
    app.state.bm25_indexes = all_bm25_indexes

    logger.info(
    "Upload completed | files=%d",
    len(files)
    )

    return {"message" : "PDF uploaded and processed succesfully. Index created"}

def normalize_query(query):
    return query.lower().strip()


r = redis.Redis(host = os.getenv("REDIS_HOST" , "redis") , 
                port = int(os.getenv("REDIS_PORT" ,6379)) , db = 0)
@app.post("/query/{query}")
def query_response(query : str):

    start_time = time.perf_counter()

    logger.info("Query received")

    if not hasattr(app.state , "chunks"):
        return {"error" : "Please Upload the PDF before querying"}

    app.state.query = query

    normalized_query = normalize_query(query)

    cached = r.get(normalized_query)

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
    
    all_chunks = app.state.chunks
    
    all_faiss_indexes = app.state.faiss_indexes

    all_bm25_indexes = app.state.bm25_indexes

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

    r.setex(normalized_query , 300 , response)

    elapsed = time.perf_counter() - start_time

    logger.info(
        "Query completed | cached=False | time=%.3fs",
        elapsed
    )

    return {
            "response" : response ,
            "cached" : False
           }


@app.get("/evaluate")
def evaluate_response():

    logger.info("Evaluation started")

    if not hasattr(app.state , "retrieved_chunks"):
        return {"error" : "Please pass a query before evaluation."}

    retrieved_chunks = app.state.retrieved_chunks

    chunk_content = [chunk["text"] for chunk in retrieved_chunks]

    coherence = evaluate_coherence(chunk_content)

    logger.info("Coherence metric completed")

    window_coherence = evaluate_window_coherence(chunk_content)

    logger.info("windowed coherence metric completed")

    readability = evaluate_readability(chunk_content)

    logger.info("readability metric completed")

    query = app.state.query

    response = app.state.response

    logger.info("DeepEval started")

    metrics = evaluate_RAG(query , chunk_content , response)

    logger.info("DeepEval completed")

    logger.info("Evaluation completed")

    return {
           "Coherence" : coherence , 
           "Window coherence for slow context drifting" : window_coherence ,
           "Readability score" : readability ,
           "Deep Eval Metrics" : metrics
           }
