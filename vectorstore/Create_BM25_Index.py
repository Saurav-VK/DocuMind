#!/usr/bin/env python
# coding: utf-8

# In[1]:


from rank_bm25 import BM25Okapi

def create_bm25_index(chunks):
    tokenized_chunks = []

    for chunk in chunks:
        tokenized_chunks.append(chunk["text"].lower().split())

    bm25 = BM25Okapi(tokenized_chunks)

    return bm25

