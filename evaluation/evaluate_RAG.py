#!/usr/bin/env python
# coding: utf-8

# In[1]:


from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
from deepeval_ollama import OllamaJudge
import os

def evaluate_RAG(query , context , answer):

    judge = OllamaJudge()

    test_case = LLMTestCase(input = query , actual_output = answer , retrieval_context = context)

    metrics = [FaithfulnessMetric(model = judge) , AnswerRelevancyMetric(model = judge)]

    results = {}
    
    for metric in metrics:

        metric.measure(test_case)
        results[metric.__class__.__name__] = metric.score

    return results

