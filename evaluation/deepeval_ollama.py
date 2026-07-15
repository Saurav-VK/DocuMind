#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from deepeval.models import DeepEvalBaseLLM
import os


class OllamaJudge(DeepEvalBaseLLM):

    def __init__(self):

        self.host = os.getenv("OLLAMA_HOST", "localhost")
        self.port = os.getenv("OLLAMA_PORT", "11434")
        self.model = os.getenv("MODEL_NAME", "mistral")

    def load_model(self):
        return self.model

    def get_model_name(self):
        return self.model

    def generate(self, prompt: str):

        response = requests.post(
            f"http://{self.host}:{self.port}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"]

    async def a_generate(self, prompt: str):
        return self.generate(prompt)

