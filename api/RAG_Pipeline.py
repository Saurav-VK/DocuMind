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
import redis

# In[4]:


from fastapi import FastAPI

app = FastAPI()

@app.post("/upload/{folder_path:path}/{strategy}")
def upload_and_store(folder_path : str , strategy : str):
    
    content = load_multiple_pdfs(folder_path)

    pages = [page for page in content if is_valid_page(page)]

    chunks = text_chunker(pages , strategy = strategy)

    chunks = [chunk for chunk in chunks if is_valid_chunk(chunk)]

    app.state.chunks = chunks

    bm25_index = create_bm25_index(chunks)

    index = create_vector_store(chunks)

    app.state.index = index

    app.state.bm25_index = bm25_index

    return {"message" : "PDF uploaded succesfully. Index created"}

def normalize_query(query):
    return query.lower().strip()


r = redis.Redis(host = "localhost" , port = 6379 , db = 0)
@app.post("/query/{query}")
def query_response(query : str):
    if not hasattr(app.state , "chunks"):
        return {"error" : "Please Upload the PDF before querying"}

    normalized_query = normalize_query(query)

    cached = r.get(normalized_query)

    if cached:
        return {
               "response" : cached.decode() ,
               "cached" : True
               }
    
    chunks = app.state.chunks
    
    index = app.state.index

    bm25_index = app.state.bm25_index

    results_faiss = retrieve_chunks(query , chunks , index)

    results_bm25 = bm25_retreival(normalized_query , bm25_index , chunks , k = 5)

    results = reciprocal_rank_fusion(results_faiss , results_bm25)

    app.state.retrieved_chunks = results

    cleaned_results = [clean_for_llm(result) for result in results]

    print(cleaned_results)

    response = answer_query(query , cleaned_results)

    r.setex(normalized_query , 300 , response)

    return {
            "response" : response ,
            "cached" : False
           }


@app.get("/evaluate")
def evaluate_response():
    if not hasattr(app.state , "retrieved_chunks"):
        return {"error" : "Please pass a query before evaluation."}

    retrieved_chunks = app.state.retrieved_chunks

    chunk_content = [chunk["text"] for chunk in retrieved_chunks]

    coherence = evaluate_coherence(chunk_content)

    window_coherence = evaluate_window_coherence(chunk_content)

    readability = evaluate_readability(chunk_content)

    return {
           "Coherence" : coherence , 
           "Window coherence for slow context drifting" : window_coherence ,
           "Readability score" : readability
           }
