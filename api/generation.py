#!/usr/bin/env python
# coding: utf-8

# In[5]:


def build_context(cleaned_chunks):
    "\n\n".join(cleaned_chunks[:2])


# In[4]:


import requests

def generate_answer(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]


# In[3]:


def answer_query(query , cleaned_chunks):
    context = build_context(cleaned_chunks)

    prompt = f"""
            You are an AI assistant.
            
            Answer the question ONLY using the context below.
            Do NOT use outside knowledge.
            
            Context:
            {context}
            
            Question: {query}
            
            Answer clearly and concisely.
            If the answer is not in the context, say: "Not found in document".
            """

    return generate_answer(prompt)


# In[ ]:




