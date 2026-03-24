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


# In[4]:


from fastapi import FastAPI

app = FastAPI()

@app.post("/upload/{pdf_path}/{strategy}")
def upload_and_store(pdf_path : str , strategy : str):
    global index , chunks
    
    content = load_pdf_text(pdf_path)

    pages = [page for page in content if is_valid_page(page)]

    chunks = text_chunker(pages , strategy = strategy)

    chunks = [chunk for chunk in chunks if is_valid_chunk(chunk)]

    index = create_vector_store(chunks)

    return {"message" : "PDF uploaded successfully"}


# In[8]:


@app.post("/ask_query/{query}")
def ask_query(query : str):
    results = retrieve_chunks(query , chunks = chunks , index = index)

    cleaned_results = [clean_for_llm(result) for result in results]

    response = answer_query(query , cleaned_results)
    
    return {"response" : response}


# In[ ]:




