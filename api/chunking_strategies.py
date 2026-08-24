#!/usr/bin/env python
# coding: utf-8

# In[3]:


from langchain_text_splitters import TokenTextSplitter
from langchain_text_splitters import SentenceTransformersTokenTextSplitter
from sentence_transformers import SentenceTransformer
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter


class ChunkingStrategies:

    def token_text_splitter(self , text , chunk_size = 200 , chunk_overlap = 40):
        splitter = TokenTextSplitter(chunk_size = chunk_size, chunk_overlap = chunk_overlap)
        
        return splitter.split_text(text)

    def sentence_transformer_token_text_splitter(self , text):
        splitter = SentenceTransformersTokenTextSplitter(chunk_size = 100)
        return splitter.split_text(text)

    def semantic_chunker(self , text):
        splitter = SemanticChunker(HuggingFaceEmbeddings())
        return splitter.split_text(text)

    def recursive_character_text_splitter(self , text , chunk_size = 100 , chunk_overlap = 40):
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size = chunk_size , chunk_overlap = chunk_overlap)
        return splitter.split_text(text)



# In[ ]:




