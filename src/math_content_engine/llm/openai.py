"""
OpenAI LLM client implementation.
"""

from typing import Optional

import openai

from .base import BaseLLMClient, LLMResponse


class OpenAIClient(BaseLLMClient):
    """LLM client for OpenAI models."""

    def __init__(self, api_key: str, model: str = "gpt-4o",
                 temperature: float = 0.7, max_tokens: int = 4096):
        super().__init__(api_key, model, temperature, max_tokens)
        self.client = openai.OpenAI(api_key=api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generate a response using OpenAI."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )

        choice = response.choices[0]
        return LLMResponse(
            content=choice.message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            finish_reason=choice.finish_reason,
        )

    def generate_with_retry(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        error_context: Optional[str] = None
    ) -> LLMResponse:
        """Generate a response with error context for code correction."""
        if error_context:
            retry_prompt = f"""{prompt}

---
PREVIOUS ATTEMPT FAILED WITH ERROR:
{error_context}

Please fix the code to resolve this error. Return ONLY the corrected Python code."""
        else:
            retry_prompt = prompt

        return self.generate(retry_prompt, system_prompt)
