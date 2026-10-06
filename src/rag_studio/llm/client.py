"""OpenRouter client (OpenAI-compatible API)."""
from typing import Protocol

import openai
from openai import OpenAI

from rag_studio.domain.errors import LlmError


class LlmClient(Protocol):
    def complete(self, system: str, user: str, model: str) -> str: ...


class OpenRouterClient:
    def __init__(self, api_key: str, base_url: str, timeout: int) -> None:
        self._client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            default_headers={"X-Title": "RAG Studio"},
        )

    def complete(self, system: str, user: str, model: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=model,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
        except openai.AuthenticationError as error:
            raise LlmError("OpenRouter rejected the API key. Check OPENROUTER_API_KEY.") from error
        except openai.NotFoundError as error:
            raise LlmError(
                f"Model '{model}' was not found on OpenRouter. Check FAST_MODEL / STRONG_MODEL in .env."
            ) from error
        except openai.RateLimitError as error:
            raise LlmError("OpenRouter rate limit reached. Wait a moment and try again.") from error
        except openai.APITimeoutError as error:
            raise LlmError("The model took too long to respond.") from error
        except openai.APIConnectionError as error:
            raise LlmError("Could not connect to OpenRouter. Check your internet connection.") from error
        except openai.APIStatusError as error:
            if error.status_code == 402:
                raise LlmError("OpenRouter says the account is out of credits.") from error
            raise LlmError(f"OpenRouter returned an error (status {error.status_code}).") from error
        return self._extract_text(response)

    @staticmethod
    def _extract_text(response) -> str:
        if not response.choices or not response.choices[0].message.content:
            raise LlmError("The model returned an empty response.")
        return response.choices[0].message.content