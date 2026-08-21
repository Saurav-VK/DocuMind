#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import pickle
import faiss
import json

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

def save_metadata(document_dir, filename, document_hash, strategy):

    metadata = {
        "filename": filename,
        "document_hash": document_hash,
        "strategy": strategy
    }

    file_path = os.path.join(
        document_dir,
        "metadata.json"
    )

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

def load_metadata(document_dir):

    file_path = os.path.join(
        document_dir,
        "metadata.json"
    )

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
    

