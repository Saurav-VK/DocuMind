#!/usr/bin/env python
# coding: utf-8

# In[1]:


from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def reranker_function(query , chunks):
    pairs = []

    for chunk in chunks:
        pairs.append(
            (
                query , chunk["text"]
            )
                    )

    scores = reranker.predict(pairs)

    for chunk , score in zip(chunks , scores):
        chunk["cross_encoder_score"] = score

    reranked_chunks = sorted(
                             chunks , key = lambda x : x["cross_encoder_score"] , reverse = True
                            )

    return reranked_chunks[:3]

