# src/library/llm.py
# Raw OpenAI SDK — no LangChain
from openai import OpenAI
from src.utils.config import OPENAI_API_KEY, MODEL_NAME

_client = OpenAI(api_key=OPENAI_API_KEY)


class LLM:
    """
    Thin wrapper around the OpenAI chat completions endpoint.
    Exposes an .invoke(prompt) interface used throughout the nodes,
    and an .invoke_vision(messages) interface for image description.
    """

    def invoke(self, prompt: str) -> "LLMResponse":
        response = _client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return LLMResponse(response.choices[0].message.content)

    def invoke_vision(self, messages: list) -> "LLMResponse":
        """
        Send a list of OpenAI message dicts directly.
        Used for multimodal (image + text) requests.
        """
        response = _client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0
        )
        return LLMResponse(response.choices[0].message.content)


class LLMResponse:
    """Mirrors the .content attribute used across all nodes."""
    def __init__(self, content: str):
        self.content = content


# Module-level singleton — imported by all nodes
llm = LLM()
