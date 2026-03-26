#!/usr/bin/env python
# coding: utf-8

# In[1]:


from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np
import textstat

encoder = SentenceTransformer("all-MiniLM-L6-v2")        


# In[2]:


def evaluate_coherence(chunks):    
    embeddings = encoder.encode(chunks)
    
    similarities = []

    if len(chunks) == 0:
        return 0.0
    
    for i in range(len(chunks) - 1):
        similarities.append(cosine_similarity([embeddings[i]] , [embeddings[i + 1]])[0][0])
    
    coherence = np.mean(similarities)
    
    return float(coherence)


# In[3]:


def evaluate_window_coherence(chunks):    
    embeddings = encoder.encode(chunks)
    
    similarities = []

    if len(chunks) == 0:
        return 0.0
    
    for i in range(1 , len(chunks)):
        previous_context = np.mean(embeddings[:i] , axis = 0).reshape(1 , -1)
        current_context = [embeddings[i]]
        similarities.append(cosine_similarity(previous_context , current_context)[0][0])

    window_coherence = np.mean(similarities)

    return float(window_coherence)


# In[4]:


def evaluate_readability(chunks):
    readability_scores = []

    if len(chunks) == 0:
        return 0.0
    
    for chunk in chunks:
        if chunk.strip():
            readability_scores.append(textstat.flesch_reading_ease(chunk))

    readability_score = np.mean(readability_scores)

    return float(readability_score)
    


# In[ ]:




