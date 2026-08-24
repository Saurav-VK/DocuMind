#!/usr/bin/env python
# coding: utf-8

# In[1]:

from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
from deepeval_ollama import OllamaJudge
from deepeval_gemini import GeminiJudge
import os

def evaluate_RAG(query , context , answer):

    eval_provider = os.getenv("EVAL_PROVIDER", "gemini")

    if eval_provider == "ollama":
        judge = OllamaJudge()

    elif eval_provider == "gemini":
        judge = GeminiJudge()

    test_case = LLMTestCase(input = query , actual_output = answer , retrieval_context = context)

    metrics = [FaithfulnessMetric(model = judge) , AnswerRelevancyMetric(model = judge)]

    results = {}
    
    for metric in metrics:
        print(f"Running {metric.__class__.__name__}")
  
        metric.measure(test_case)

        print(f"{metric.__class__.__name__} completed")

        results[metric.__class__.__name__] = metric.score

    return results
