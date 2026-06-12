#!/usr/bin/env python
# coding: utf-8

# In[1]:


def reciprocal_rank_fusion(faiss , bm25):
    k = 60

    rrf_scores = {}
    chunk_lookup = {}

    for rank , chunk in enumerate(faiss , start = 1):
        chunk_id = chunk["id"]

        rrf_scores[chunk_id] = (rrf_scores.get(chunk_id , 0) + (1 / (k + rank)))

        chunk_lookup[chunk_id] = chunk

    for rank , chunk in enumerate(bm25 , start = 1):
        chunk_id = chunk["id"]

        rrf_scores[chunk_id] = (rrf_scores.get(chunk_id , 0) + (1 / (k + rank)))

        chunk_lookup[chunk_id] = chunk

    results = []

    ranked_chunks = sorted(
                           rrf_scores.items() ,
                           key = lambda x : x[1] ,
                           reverse = True
                           )

    for chunk_id , score in ranked_chunks:
        chunk = chunk_lookup[chunk_id].copy()
        chunk["rrf_score"] = score
        results.append(chunk)

    return results


# In[ ]:




