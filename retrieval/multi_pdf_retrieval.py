#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from retrieval import retrieve_chunks
from BM25_retreival import bm25_retreival

def retrieve_from_multiple_pdfs(
    query,
    all_chunks,
    all_faiss_indexes,
    all_bm25_indexes,
    k=5
):

    all_faiss_results = []
    all_bm25_results = []

    for chunks , faiss_index , bm25_index in zip(all_chunks , all_faiss_indexes , all_bm25_indexes):

        faiss_results = retrieve_chunks(
            query,
            chunks,
            faiss_index,
            k=k
        )

        bm25_results = bm25_retreival(
            query.lower().strip(),
            bm25_index,
            chunks,
            k=k
        )

        all_faiss_results.extend(faiss_results)
        all_bm25_results.extend(bm25_results)

    return all_faiss_results , all_bm25_results

