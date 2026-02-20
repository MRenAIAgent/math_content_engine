"""
DeepSeek LLM client implementation.

Uses the OpenAI-compatible API at https://api.deepseek.com.
The deepseek-reasoner model returns chain-of-thought reasoning
in a separate `reasoning_content` field before the final answer.
"""

import logging
from typing import Optional

import openai

from .base import BaseLLMClient, LLMResponse

logger = logging.getLogger(__name__)

DEEPSEEK_BASE_URL = "https://api.deepseek.com"


class DeepSeekClient(BaseLLMClient):
    """LLM client for DeepSeek models via OpenAI-compatible API."""

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-reasoner",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        super().__init__(api_key=api_key, model=model, temperature=temperature, max_tokens=max_tokens)
        self.client = openai.OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        *,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Generate a response using DeepSeek.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            max_tokens: Override the default max_tokens if provided
            temperature: Override the default temperature if provided
            json_mode: Request structured JSON output via response_format.
                Only applies to deepseek-chat; deepseek-reasoner does not
                support response_format.

        Note:
            deepseek-reasoner does NOT support the `temperature` parameter
            and ignores system prompts. For the reasoner model, system
            instructions are prepended to the user prompt instead.
        """
        messages = []
        is_reasoner = "reasoner" in self.model

        if system_prompt:
            if is_reasoner:
                # deepseek-reasoner does not support system role messages;
                # prepend system instructions to the user prompt.
                prompt = f"{system_prompt}\n\n---\n\n{prompt}"
            else:
                messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        # Build kwargs — reasoner does not accept temperature
        kwargs = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens if max_tokens is not None else self.max_tokens,
        }
        if not is_reasoner:
            kwargs["temperature"] = temperature if temperature is not None else self.temperature

        # deepseek-chat supports response_format; deepseek-reasoner does not.
        if json_mode and not is_reasoner:
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)

        choice = response.choices[0]

        # deepseek-reasoner returns reasoning_content alongside the answer
        reasoning = getattr(choice.message, "reasoning_content", None)
        if reasoning:
            logger.debug("DeepSeek reasoning (%d chars): %.200s...", len(reasoning), reasoning)

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
        error_context: Optional[str] = None,
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
