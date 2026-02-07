"""
Tests for Mathpix PDF parser.

These tests require MATHPIX_APP_ID and MATHPIX_APP_KEY to be set.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from math_content_engine.personalization.pdf_parser import (
    MathpixPDFParser,
    MathpixConfig,
    parse_textbook_pdf,
)


@pytest.fixture
def mock_mathpix_config():
    """Create a mock Mathpix configuration."""
    return MathpixConfig(
        app_id="test_app_id",
        app_key="test_app_key"
    )


@pytest.fixture
def pdf_parser(mock_mathpix_config):
    """Create a PDF parser with mock config."""
    return MathpixPDFParser(mock_mathpix_config)


class TestMathpixConfig:
    """Test MathpixConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = MathpixConfig(app_id="test_id", app_key="test_key")
        assert config.app_id == "test_id"
        assert config.app_key == "test_key"
        assert config.api_url == "https://api.mathpix.com/v3/pdf"
        assert config.conversion_formats["md"] is True

    def test_from_env_missing_credentials(self):
        """Test that from_env raises error when credentials missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Mathpix credentials not found"):
                MathpixConfig.from_env()

    def test_from_env_with_credentials(self):
        """Test from_env with credentials set."""
        with patch.dict(os.environ, {
            "MATHPIX_APP_ID": "env_app_id",
            "MATHPIX_APP_KEY": "env_app_key"
        }):
            config = MathpixConfig.from_env()
            assert config.app_id == "env_app_id"
            assert config.app_key == "env_app_key"


class TestMathpixPDFParser:
    """Test MathpixPDFParser class."""

    def test_parser_initialization(self, pdf_parser, mock_mathpix_config):
        """Test parser initializes correctly."""
        assert pdf_parser.config == mock_mathpix_config
        assert pdf_parser.headers["app_id"] == "test_app_id"
        assert pdf_parser.headers["app_key"] == "test_app_key"

    def test_from_env(self):
        """Test creating parser from environment."""
        with patch.dict(os.environ, {
            "MATHPIX_APP_ID": "env_id",
            "MATHPIX_APP_KEY": "env_key"
        }):
            parser = MathpixPDFParser.from_env()
            assert parser.config.app_id == "env_id"
            assert parser.config.app_key == "env_key"

    def test_parse_pdf_file_not_found(self, pdf_parser):
        """Test that parse_pdf raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            pdf_parser.parse_pdf("nonexistent.pdf")

    @patch('math_content_engine.personalization.pdf_parser.requests.post')
    @patch('math_content_engine.personalization.pdf_parser.requests.get')
    def test_parse_pdf_success(self, mock_get, mock_post, pdf_parser, tmp_path):
        """Test successful PDF parsing."""
        # Create a dummy PDF file
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"PDF content")

        # Mock upload response
        mock_post.return_value.json.return_value = {"pdf_id": "test_pdf_id"}
        mock_post.return_value.raise_for_status = Mock()

        # Mock status check response
        mock_get.return_value.json.return_value = {
            "status": "completed",
            "percent_done": 100,
            "md": "https://mathpix.com/result.md"
        }
        mock_get.return_value.raise_for_status = Mock()
        mock_get.return_value.text = "# Markdown content"

        result = pdf_parser.parse_pdf(str(pdf_file))

        assert result["status"] == "completed"
        assert "md" in result
        mock_post.assert_called_once()
        mock_get.assert_called()

    @patch('math_content_engine.personalization.pdf_parser.requests.post')
    @patch('math_content_engine.personalization.pdf_parser.requests.get')
    def test_parse_pdf_conversion_error(self, mock_get, mock_post, pdf_parser, tmp_path):
        """Test PDF parsing with conversion error."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"PDF content")

        # Mock upload response
        mock_post.return_value.json.return_value = {"pdf_id": "test_pdf_id"}
        mock_post.return_value.raise_for_status = Mock()

        # Mock error response
        mock_get.return_value.json.return_value = {
            "status": "error",
            "error": "Conversion failed"
        }
        mock_get.return_value.raise_for_status = Mock()

        with pytest.raises(RuntimeError, match="PDF conversion failed"):
            pdf_parser.parse_pdf(str(pdf_file))

    @patch('math_content_engine.personalization.pdf_parser.requests.post')
    @patch('math_content_engine.personalization.pdf_parser.requests.get')
    def test_parse_pdf_timeout(self, mock_get, mock_post, pdf_parser, tmp_path):
        """Test PDF parsing timeout."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"PDF content")

        # Mock upload response
        mock_post.return_value.json.return_value = {"pdf_id": "test_pdf_id"}
        mock_post.return_value.raise_for_status = Mock()

        # Mock status that never completes
        mock_get.return_value.json.return_value = {
            "status": "processing",
            "percent_done": 50
        }
        mock_get.return_value.raise_for_status = Mock()

        with pytest.raises(TimeoutError):
            # Use very short timeout for test
            pdf_parser._wait_for_conversion("test_id", max_wait_seconds=1, poll_interval=0.1)

    @patch('math_content_engine.personalization.pdf_parser.requests.get')
    def test_get_markdown_from_result(self, mock_get, pdf_parser):
        """Test extracting markdown from result."""
        result = {"md": "https://mathpix.com/result.md"}
        mock_get.return_value.text = "# Test Markdown"
        mock_get.return_value.raise_for_status = Mock()

        markdown = pdf_parser.get_markdown_from_result(result)

        assert markdown == "# Test Markdown"
        mock_get.assert_called_once()

    def test_get_markdown_from_result_no_url(self, pdf_parser):
        """Test get_markdown_from_result raises error when no URL."""
        result = {"status": "completed"}

        with pytest.raises(ValueError, match="No markdown URL"):
            pdf_parser.get_markdown_from_result(result)


class TestParseFunctions:
    """Test convenience functions."""

    @patch('math_content_engine.personalization.pdf_parser.MathpixPDFParser')
    def test_parse_textbook_pdf(self, mock_parser_class, tmp_path):
        """Test parse_textbook_pdf convenience function."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"PDF content")
        output_path = tmp_path / "output.md"

        # Mock parser
        mock_parser = MagicMock()
        mock_parser.parse_pdf_to_markdown.return_value = "# Markdown"
        mock_parser_class.from_env.return_value = mock_parser

        result = parse_textbook_pdf(str(pdf_path), str(output_path))

        assert result == "# Markdown"
        mock_parser.parse_pdf_to_markdown.assert_called_once()


@pytest.mark.e2e
@pytest.mark.skipif(
    not os.getenv("MATHPIX_APP_ID") or not os.getenv("MATHPIX_APP_KEY"),
    reason="Mathpix credentials not set"
)
class TestMathpixE2E:
    """
    End-to-end tests with real Mathpix API.

    These tests require valid MATHPIX_APP_ID and MATHPIX_APP_KEY.
    """

    def test_real_pdf_parsing(self, tmp_path):
        """Test parsing a real PDF (if credentials are set)."""
        # This would need a real PDF file to test
        # Skip for now unless you have a test PDF
        pytest.skip("Requires test PDF file")
