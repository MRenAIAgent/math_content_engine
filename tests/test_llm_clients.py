"""Tests for LLM client implementations."""

import pytest
from unittest.mock import Mock, patch
from math_content_engine.llm.base import BaseLLMClient, LLMResponse
from math_content_engine.llm.claude import ClaudeClient
from math_content_engine.llm.openai import OpenAIClient
from math_content_engine.llm.factory import create_llm_client
from math_content_engine.constants import LLMProvider


class TestBaseLLMClient:
    """Tests for BaseLLMClient abstract class."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that BaseLLMClient cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseLLMClient(api_key="test", model="test")


class TestLLMResponse:
    """Tests for LLMResponse dataclass."""

    def test_response_creation(self):
        """Test creating LLMResponse."""
        response = LLMResponse(
            content="Generated code",
            model="claude-sonnet-4-20250514",
            usage={"input_tokens": 100, "output_tokens": 200},
            finish_reason="end_turn"
        )
        assert response.content == "Generated code"
        assert response.model == "claude-sonnet-4-20250514"
        assert response.usage["input_tokens"] == 100
        assert response.finish_reason == "end_turn"


class TestClaudeClient:
    """Tests for ClaudeClient implementation."""

    def test_initialization(self):
        """Test Claude client initialization."""
        client = ClaudeClient(
            api_key="test-key",
            model="claude-sonnet-4-20250514",
            temperature=0.7,
            max_tokens=4096
        )
        assert client.model == "claude-sonnet-4-20250514"
        assert client.temperature == 0.7
        assert client.max_tokens == 4096

    @patch('anthropic.Anthropic')
    def test_generate_success(self, mock_anthropic_class):
        """Test successful code generation."""
        # Setup mock
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        mock_message = Mock()
        mock_message.content = [Mock(text="Generated code here")]
        mock_message.model = "claude-sonnet-4-20250514"
        mock_message.usage = Mock(input_tokens=100, output_tokens=200)
        mock_message.stop_reason = "end_turn"

        mock_client.messages.create.return_value = mock_message

        # Test
        client = ClaudeClient(api_key="test-key", model="claude-sonnet-4-20250514")
        result = client.generate("Write a math animation")

        # Verify - returns LLMResponse
        assert isinstance(result, LLMResponse)
        assert result.content == "Generated code here"
        assert result.model == "claude-sonnet-4-20250514"
        assert result.usage['input_tokens'] == 100
        assert result.usage['output_tokens'] == 200

        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs['model'] == "claude-sonnet-4-20250514"
        assert call_kwargs['max_tokens'] == 4096
        assert len(call_kwargs['messages']) == 1
        assert call_kwargs['messages'][0]['content'] == "Write a math animation"

    @patch('anthropic.Anthropic')
    def test_generate_with_system_prompt(self, mock_anthropic_class):
        """Test generation with system prompt."""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        mock_message = Mock()
        mock_message.content = [Mock(text="Code")]
        mock_message.model = "claude-sonnet-4-20250514"
        mock_message.usage = Mock(input_tokens=100, output_tokens=200)
        mock_message.stop_reason = "end_turn"

        mock_client.messages.create.return_value = mock_message

        client = ClaudeClient(api_key="test-key", model="claude-sonnet-4-20250514")
        client.generate("Prompt", system_prompt="You are a math expert")

        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs['system'] == "You are a math expert"

    @patch('anthropic.Anthropic')
    def test_generate_with_retry_error_context(self, mock_anthropic_class):
        """Test generation with retry and error context."""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        mock_message = Mock()
        mock_message.content = [Mock(text="Fixed code")]
        mock_message.model = "claude-sonnet-4-20250514"
        mock_message.usage = Mock(input_tokens=150, output_tokens=250)
        mock_message.stop_reason = "end_turn"

        mock_client.messages.create.return_value = mock_message

        client = ClaudeClient(api_key="test-key", model="claude-sonnet-4-20250514")
        result = client.generate_with_retry(
            "Write a math animation",
            error_context="Previous error: SyntaxError on line 5"
        )

        assert isinstance(result, LLMResponse)
        assert result.content == "Fixed code"

        # Check that error context is included in prompt
        call_kwargs = mock_client.messages.create.call_args[1]
        prompt = call_kwargs['messages'][0]['content']
        assert "Write a math animation" in prompt
        assert "PREVIOUS ATTEMPT FAILED WITH ERROR" in prompt
        assert "SyntaxError on line 5" in prompt
        assert "Please fix the code" in prompt

    @patch('anthropic.Anthropic')
    def test_api_error_handling(self, mock_anthropic_class):
        """Test handling of API errors."""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API Error")

        client = ClaudeClient(api_key="test-key", model="claude-sonnet-4-20250514")

        with pytest.raises(Exception, match="API Error"):
            client.generate("Write a math animation")


class TestOpenAIClient:
    """Tests for OpenAIClient implementation."""

    def test_initialization(self):
        """Test OpenAI client initialization."""
        client = OpenAIClient(
            api_key="test-key",
            model="gpt-4o",
            temperature=0.8,
            max_tokens=2048
        )
        assert client.model == "gpt-4o"
        assert client.temperature == 0.8
        assert client.max_tokens == 2048

    @patch('openai.OpenAI')
    def test_generate_success(self, mock_openai_class):
        """Test successful code generation."""
        # Setup mock
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_choice = Mock()
        mock_choice.message.content = "Generated OpenAI code"
        mock_choice.finish_reason = "stop"

        mock_response = Mock()
        mock_response.model = "gpt-4o"
        mock_response.choices = [mock_choice]
        mock_response.usage = Mock(prompt_tokens=100, completion_tokens=200, total_tokens=300)

        mock_client.chat.completions.create.return_value = mock_response

        # Test
        client = OpenAIClient(api_key="test-key", model="gpt-4o")
        result = client.generate("Write a math animation")

        # Verify - returns LLMResponse
        assert isinstance(result, LLMResponse)
        assert result.content == "Generated OpenAI code"
        assert result.model == "gpt-4o"
        assert result.usage['prompt_tokens'] == 100
        assert result.usage['completion_tokens'] == 200

        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['model'] == "gpt-4o"
        assert call_kwargs['max_tokens'] == 4096
        assert len(call_kwargs['messages']) == 1  # user only (no system prompt provided)
        assert call_kwargs['messages'][0]['role'] == 'user'
        assert call_kwargs['messages'][0]['content'] == "Write a math animation"

    @patch('openai.OpenAI')
    def test_generate_with_retry_error_context(self, mock_openai_class):
        """Test generation with retry and error context."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_choice = Mock()
        mock_choice.message.content = "Fixed OpenAI code"
        mock_choice.finish_reason = "stop"

        mock_response = Mock()
        mock_response.model = "gpt-4o"
        mock_response.choices = [mock_choice]
        mock_response.usage = Mock(prompt_tokens=150, completion_tokens=250, total_tokens=400)

        mock_client.chat.completions.create.return_value = mock_response

        client = OpenAIClient(api_key="test-key", model="gpt-4o")
        result = client.generate_with_retry(
            "Write a math animation",
            error_context="Previous error: TypeError"
        )

        assert isinstance(result, LLMResponse)
        assert result.content == "Fixed OpenAI code"

        call_kwargs = mock_client.chat.completions.create.call_args[1]
        prompt = call_kwargs['messages'][0]['content']  # user message (no system prompt provided)
        assert "Write a math animation" in prompt
        assert "PREVIOUS ATTEMPT FAILED WITH ERROR" in prompt
        assert "TypeError" in prompt


class TestLLMFactory:
    """Tests for LLM client factory."""

    @patch('math_content_engine.llm.factory.ClaudeClient')
    def test_create_claude_client(self, mock_claude_class):
        """Test creating Claude client via factory."""
        mock_config = Mock()
        mock_config.llm_provider = LLMProvider.CLAUDE
        mock_config.anthropic_api_key = "claude-key"
        mock_config.claude_model = "claude-sonnet-4-20250514"
        mock_config.temperature = 0.7
        mock_config.max_tokens = 4096

        client = create_llm_client(mock_config)

        mock_claude_class.assert_called_once_with(
            api_key="claude-key",
            model="claude-sonnet-4-20250514",
            temperature=0.7,
            max_tokens=4096
        )

    @patch('math_content_engine.llm.factory.OpenAIClient')
    def test_create_openai_client(self, mock_openai_class):
        """Test creating OpenAI client via factory."""
        mock_config = Mock()
        mock_config.llm_provider = LLMProvider.OPENAI
        mock_config.openai_api_key = "openai-key"
        mock_config.openai_model = "gpt-4o"
        mock_config.temperature = 0.8
        mock_config.max_tokens = 2048

        client = create_llm_client(mock_config)

        mock_openai_class.assert_called_once_with(
            api_key="openai-key",
            model="gpt-4o",
            temperature=0.8,
            max_tokens=2048
        )

    def test_invalid_provider_raises(self):
        """Test that invalid provider raises ValueError."""
        mock_config = Mock()
        mock_config.llm_provider = "invalid_provider"

        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            create_llm_client(mock_config)


class TestRetryBehavior:
    """Tests for retry behavior across LLM clients."""

    @patch('anthropic.Anthropic')
    def test_claude_retry_format(self, mock_anthropic_class):
        """Test Claude retry prompt formatting."""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        mock_message = Mock()
        mock_message.content = [Mock(text="Fixed")]
        mock_message.model = "claude-sonnet-4-20250514"
        mock_message.usage = Mock(input_tokens=100, output_tokens=200)
        mock_message.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_message

        client = ClaudeClient(api_key="test-key", model="claude-sonnet-4-20250514")
        client.generate_with_retry("Original prompt", error_context="Error: Line 5")

        prompt = mock_client.messages.create.call_args[1]['messages'][0]['content']

        # Check retry format
        assert "Original prompt" in prompt
        assert "---" in prompt
        assert "PREVIOUS ATTEMPT FAILED WITH ERROR:" in prompt
        assert "Error: Line 5" in prompt
        assert "Please fix the code" in prompt

    @patch('openai.OpenAI')
    def test_openai_retry_format(self, mock_openai_class):
        """Test OpenAI retry prompt formatting."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_choice = Mock()
        mock_choice.message.content = "Fixed"
        mock_choice.finish_reason = "stop"
        mock_response = Mock()
        mock_response.model = "gpt-4o"
        mock_response.choices = [mock_choice]
        mock_response.usage = Mock(prompt_tokens=100, completion_tokens=200, total_tokens=300)
        mock_client.chat.completions.create.return_value = mock_response

        client = OpenAIClient(api_key="test-key", model="gpt-4o")
        client.generate_with_retry("Original prompt", error_context="Error: Line 10")

        prompt = mock_client.chat.completions.create.call_args[1]['messages'][0]['content']  # user message

        # Check retry format (should match Claude)
        assert "Original prompt" in prompt
        assert "---" in prompt
        assert "PREVIOUS ATTEMPT FAILED WITH ERROR:" in prompt
        assert "Error: Line 10" in prompt
        assert "Please fix the code" in prompt


class TestClientInterface:
    """Tests for client interface consistency."""

    def test_claude_implements_base_interface(self):
        """Test that ClaudeClient implements BaseLLMClient."""
        assert issubclass(ClaudeClient, BaseLLMClient)

    def test_openai_implements_base_interface(self):
        """Test that OpenAIClient implements BaseLLMClient."""
        assert issubclass(OpenAIClient, BaseLLMClient)

    def test_both_clients_have_generate_method(self):
        """Test that both clients have generate method."""
        claude = ClaudeClient(api_key="test", model="test")
        openai = OpenAIClient(api_key="test", model="test")

        assert hasattr(claude, 'generate')
        assert callable(claude.generate)
        assert hasattr(openai, 'generate')
        assert callable(openai.generate)

    def test_both_clients_have_generate_with_retry(self):
        """Test that both clients have generate_with_retry method."""
        claude = ClaudeClient(api_key="test", model="test")
        openai = OpenAIClient(api_key="test", model="test")

        assert hasattr(claude, 'generate_with_retry')
        assert callable(claude.generate_with_retry)
        assert hasattr(openai, 'generate_with_retry')
        assert callable(openai.generate_with_retry)
