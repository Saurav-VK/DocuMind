#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import pickle
import faiss

def save_chunks(chunks , document_dir):
    file_path = os.path.join(document_dir , "chunks.pkl")

    with open(file_path , "wb") as f:
        pickle.dump(chunks , f)


def load_chunks(document_dir):
    file_path = os.path.join(document_dir , "chunks.pkl")

    with open(file_path , "rb") as f:
        chunks = pickle.load(f)

    return chunks


def save_faiss_index(index , document_dir):
    file_path = os.path.join(document_dir , "faiss.index")
    faiss.write_index(index , file_path)


def load_faiss_index(document_dir):
    file_path = os.path.join(document_dir , "faiss.index")
    return faiss.read_index(file_path)


def save_bm25_index(bm25_index , document_dir):
    file_path = os.path.join(document_dir , "bm25.pkl")
    with open (file_path , "wb") as f:
        pickle.dump(bm25_index , f)

def load_bm25_index(document_dir):
    file_path = os.path.join(document_dir , "bm25.pkl")
    with open (file_path , "rb") as f:
        return pickle.load(f)
    

