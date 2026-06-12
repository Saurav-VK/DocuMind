#!/usr/bin/env python
# coding: utf-8

# In[5]:


from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

encoder = SentenceTransformer("all-MiniLM-L6-v2")

def create_vector_store(chunks):
    text = [chunk["text"] for chunk in chunks]
    
    embeddings = encoder.encode(text , batch_size = 32 , show_progress_bar = True)
    
    dimensions = embeddings.shape[1]
    
    index = faiss.IndexFlatL2(dimensions)
    index.add(np.array(embeddings))

    return index


# In[ ]:




