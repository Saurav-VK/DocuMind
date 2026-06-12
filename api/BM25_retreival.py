#!/usr/bin/env python
# coding: utf-8

# In[13]:


def bm25_retreival(query , bm25_index , chunks , k = 5):

    scores = bm25_index.get_scores(query)

    ranked_indices = sorted(range(len(scores)) , key = lambda i : scores[i] , reverse = True)

    results = []

    for idx in ranked_indices[:k]:
        chunk = chunks[idx]

        results.append({
            "id" : chunk["id"] ,
            "text" : chunk["text"] ,
            "page" : chunk["page"] ,
            "source" : chunk["source"] ,
            "score" : float(scores[idx])
        })

    return results
        


# In[ ]:




