"""
Factory function for creating LLM clients.
"""

from ..config import Config, LLMProvider
from .base import BaseLLMClient
from .claude import ClaudeClient
from .openai import OpenAIClient


def create_llm_client(config: Config) -> BaseLLMClient:
    """
    Create an LLM client based on configuration.

    Args:
        config: Configuration object with LLM settings

    Returns:
        Configured LLM client instance

    Raises:
        ValueError: If provider is not supported
    """
    if config.llm_provider == LLMProvider.CLAUDE:
        return ClaudeClient(
            api_key=config.anthropic_api_key,
            model=config.claude_model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )
    elif config.llm_provider == LLMProvider.OPENAI:
        return OpenAIClient(
            api_key=config.openai_api_key,
            model=config.openai_model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )
    elif config.llm_provider == LLMProvider.GEMINI:
        from .gemini import GeminiClient

        return GeminiClient(
            model=config.gemini_model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            project_id=config.gcp_project_id,
            location=config.gcp_location,
        )
    elif config.llm_provider == LLMProvider.DEEPSEEK:
        from .deepseek import DeepSeekClient

        return DeepSeekClient(
            api_key=config.deepseek_api_key,
            model=config.deepseek_model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {config.llm_provider}")
