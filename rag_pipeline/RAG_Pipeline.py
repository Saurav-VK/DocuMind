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
import redis

# In[4]:


from fastapi import FastAPI

app = FastAPI()

@app.post("/upload/{pdf_path:path}/{strategy}")
def upload_and_store(pdf_path : str , strategy : str):
    
    content = load_pdf_text(pdf_path)

    pages = [page for page in content if is_valid_page(page)]

    chunks = text_chunker(pages , strategy = strategy)

    chunks = [chunk for chunk in chunks if is_valid_chunk(chunk)]

    app.state.chunks = chunks

    index = create_vector_store(chunks)

    app.state.index = index

    return {"message" : "PDF uploaded succesfully. Index created"}


r = redis.Redis(host = "localhost" , port = 6379 , db = 0)
@app.post("/query/{query}")
def query_response(query : str):
    if not hasattr(app.state , "chunks"):
        return {"error" : "Please Upload the PDF before querying"}

    cached = r.get(query)

    if cached:
        return {
               "response" : cached.decode() ,
               "cached" : True
               }
    
    chunks = app.state.chunks
    
    index = app.state.index

    results = retrieve_chunks(query , chunks , index)

    app.state.retrieved_chunks = results

    cleaned_results = [clean_for_llm(result) for result in results]

    response = answer_query(query , cleaned_results)

    r.setex(query , 300 , response)

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



