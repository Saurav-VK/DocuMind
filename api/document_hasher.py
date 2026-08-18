#!/usr/bin/env python
# coding: utf-8

# In[1]:


import hashlib

def generate_document_hash(file_path , strategy):
    hasher = hashlib.sha256()

    with open(file_path , "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)

    hasher.update(strategy.encode("utf-8"))

    return hasher.hexdigest()

