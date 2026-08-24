#!/usr/bin/env python
# coding: utf-8


from google import genai
import os
import requests
from logger import logger
from google.genai import errors
from fastapi import HTTPException


def build_context(cleaned_chunks):
    return "\n\n".join(cleaned_chunks[:2])

def generate_with_ollama(prompt):

    host = os.getenv(
        "OLLAMA_HOST",
        "host.docker.internal"
    )

    port = os.getenv(
        "OLLAMA_PORT",
        "11434"
    )

    model = os.getenv(
        "MODEL_NAME",
        "mistral"
    )

    response = requests.post(
        f"http://{host}:{port}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )

    logger.info(
    "Ollama response | status=%s | body=%s",
    response.status_code,
    response.text
    )

    response.raise_for_status()

    return response.json()["response"]

def generate_with_gemini(prompt):

    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )

    model = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.6-flash"
    )

    try:

        logger.info(
            "Gemini generation request | model=%s",
            model
        )

        response = client.models.generate_content(
            model=model,
            contents=prompt
        )

        logger.info(
            "Gemini generation completed | model=%s",
            model
        )

        return response.text

    except errors.ClientError as error:

        logger.exception("Gemini client error | status = %s",error.code)

        if error.code == 429:
            raise HTTPException(status_code = 429 , detail = "AI Service quota reached. Please try again later")

        raise HTTPException(status_code = 502 , detail = "AI service request failed.")

    except errors.ServerError as error:

        logger.exception("Gemini server error | status = %s", error.code)

        if error.code == 503:
            raise HTTPException(status_code = 503 , detail = "AI service is temporarily available due to a spike in traffic. Please try agan later.")

        raise HTTPException(status_code = 502 , detail = "AI Service is temporarily unavailable.")
        



def generate_answer(prompt):

    provider = os.getenv(
        "LLM_PROVIDER",
        "gemini"
    ).lower()

    if provider == "ollama":
        output = generate_with_ollama(prompt)

    elif provider == "gemini":
        output = generate_with_gemini(prompt)

    else:
        raise ValueError( f"Unsupported LLM provider: {provider}")
    

    print("\n" + "=" * 80)
    print(output)
    print("=" * 80 + "\n")

    return output


def answer_query(query, cleaned_chunks):

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