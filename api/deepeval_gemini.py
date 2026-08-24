import os
from google import genai
from deepeval.models import DeepEvalBaseLLM


class GeminiJudge(DeepEvalBaseLLM):

    def __init__(self):
        self.model = os.getenv(
            "GEMINI_EVAL_MODEL",
            "gemini-3.6-flash"
        )

        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

    def load_model(self):
        return self.model

    def get_model_name(self):
        return self.model

    def generate(self, prompt: str):

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        return response.text

    async def a_generate(self, prompt: str):
        return self.generate(prompt)