"""
Claude (Anthropic) LLM client implementation.
"""

from typing import Optional

import anthropic

from .base import BaseLLMClient, LLMResponse


class ClaudeClient(BaseLLMClient):
    """LLM client for Anthropic's Claude models."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514",
                 temperature: float = 0.7, max_tokens: int = 4096):
        super().__init__(api_key, model, temperature, max_tokens)
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, 
                 max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> LLMResponse:
        """Generate a response using Claude.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            max_tokens: Override the default max_tokens if provided
            temperature: Override the default temperature if provided
        """
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens if max_tokens is not None else self.max_tokens,
            "temperature": temperature if temperature is not None else self.temperature,
            "messages": messages,
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)

        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            finish_reason=response.stop_reason,
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
