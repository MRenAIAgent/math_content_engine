"""
PDF parser using Mathpix API for extracting structured mathematical content.

Mathpix provides excellent OCR for mathematical equations, tables, and text
from PDF documents, making it ideal for parsing math textbooks.
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


@dataclass
class MathpixConfig:
    """Configuration for Mathpix API."""
    app_id: str
    app_key: str
    api_url: str = "https://api.mathpix.com/v3/pdf"
    conversion_formats: Dict[str, Any] = None

    def __post_init__(self):
        if self.conversion_formats is None:
            # Default to markdown with math support
            self.conversion_formats = {
                "md": True,
                "docx": False,
                "latex_zip": False,
                "html": False
            }

    @classmethod
    def from_env(cls) -> "MathpixConfig":
        """Load Mathpix configuration from environment variables."""
        # Load environment variables from .env file
        load_dotenv()
        
        app_id = os.getenv("MATHPIX_APP_ID")
        app_key = os.getenv("MATHPIX_APP_KEY")

        if not app_id or not app_key:
            raise ValueError(
                "Mathpix credentials not found. Please set MATHPIX_APP_ID "
                "and MATHPIX_APP_KEY in your .env file"
            )

        return cls(app_id=app_id, app_key=app_key)


class MathpixPDFParser:
    """
    Parse PDF files using Mathpix API.

    Mathpix specializes in mathematical content extraction with excellent
    support for LaTeX equations, tables, and complex mathematical notation.

    Usage:
        parser = MathpixPDFParser.from_env()
        result = parser.parse_pdf("textbook.pdf")
        markdown_content = result["markdown"]
    """

    def __init__(self, config: MathpixConfig):
        """
        Initialize the parser with Mathpix configuration.

        Args:
            config: MathpixConfig with API credentials
        """
        self.config = config
        self.headers = {
            "app_id": config.app_id,
            "app_key": config.app_key
        }

    @classmethod
    def from_env(cls) -> "MathpixPDFParser":
        """Create parser from environment variables."""
        config = MathpixConfig.from_env()
        return cls(config)

    def parse_pdf(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None,
        conversion_formats: Optional[Dict[str, Any]] = None,
        page_range: Optional[str] = None,
        enable_tables_fallback: bool = True,
        enable_spell_check: bool = True,
    ) -> Dict[str, Any]:
        """
        Parse a PDF file and extract structured content.

        Args:
            pdf_path: Path to the PDF file
            output_dir: Optional directory to save extracted content
            conversion_formats: Dict specifying output formats (md, docx, latex_zip, html)
            page_range: Optional page range (e.g., "1-10", "5-", "-20")
            enable_tables_fallback: Use fallback for table extraction
            enable_spell_check: Enable spell checking

        Returns:
            Dictionary with conversion results including markdown content

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If API credentials are invalid
            requests.HTTPError: If API request fails
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        logger.info(f"Parsing PDF: {pdf_path.name}")

        # Step 1: Upload PDF and initiate conversion
        pdf_id = self._upload_pdf(pdf_path, conversion_formats, page_range,
                                   enable_tables_fallback, enable_spell_check)

        # Step 2: Poll for conversion completion
        result = self._wait_for_conversion(pdf_id)

        # Step 3: Download markdown content
        if output_dir:
            self._save_results(result, output_dir, pdf_path.stem)

        return result

    def _upload_pdf(
        self,
        pdf_path: Path,
        conversion_formats: Optional[Dict[str, Any]],
        page_range: Optional[str],
        enable_tables_fallback: bool,
        enable_spell_check: bool,
    ) -> str:
        """Upload PDF to Mathpix and start conversion."""
        url = self.config.api_url

        # Prepare conversion options
        formats = conversion_formats or self.config.conversion_formats
        options = {
            "conversion_formats": formats,
            "enable_tables_fallback": enable_tables_fallback,
            "enable_spell_check": enable_spell_check,
        }

        if page_range:
            options["page_ranges"] = page_range

        # Upload PDF
        with open(pdf_path, "rb") as f:
            files = {"file": f}
            response = requests.post(
                url,
                headers=self.headers,
                files=files,
                data={"options_json": json.dumps(options)}
            )

        response.raise_for_status()
        data = response.json()

        pdf_id = data.get("pdf_id")
        if not pdf_id:
            raise ValueError(f"Failed to upload PDF: {data}")

        logger.info(f"PDF uploaded successfully. ID: {pdf_id}")
        return pdf_id

    def _wait_for_conversion(
        self,
        pdf_id: str,
        max_wait_seconds: int = 600,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """
        Poll Mathpix API until conversion is complete.

        Args:
            pdf_id: The PDF conversion ID
            max_wait_seconds: Maximum time to wait for conversion
            poll_interval: Seconds between polling attempts

        Returns:
            Conversion result dictionary
        """
        url = f"{self.config.api_url}/{pdf_id}"
        start_time = time.time()

        logger.info("Waiting for PDF conversion to complete...")

        while True:
            elapsed = time.time() - start_time
            if elapsed > max_wait_seconds:
                raise TimeoutError(
                    f"PDF conversion timed out after {max_wait_seconds} seconds"
                )

            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            status = data.get("status")
            percent_done = data.get("percent_done", 0)

            logger.debug(f"Conversion status: {status} ({percent_done}% complete)")

            if status == "completed":
                logger.info("PDF conversion completed successfully")
                return data
            elif status == "error":
                error_msg = data.get("error", "Unknown error")
                raise RuntimeError(f"PDF conversion failed: {error_msg}")

            time.sleep(poll_interval)

    def _save_results(
        self,
        result: Dict[str, Any],
        output_dir: str,
        base_name: str
    ) -> None:
        """Save conversion results to files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save markdown (check both old and new API formats)
        md_url = None
        if "md" in result and isinstance(result["md"], str):
            md_url = result["md"]
        elif "pdf_id" in result:
            conversion_status = result.get("conversion_status", {})
            if conversion_status.get("md", {}).get("status") == "completed":
                md_url = f"{self.config.api_url}/{result['pdf_id']}.md"
        
        if md_url:
            md_content = self._download_url(md_url)
            md_file = output_path / f"{base_name}.md"
            md_file.write_text(md_content, encoding="utf-8")
            logger.info(f"Markdown saved: {md_file}")

        # Save DOCX if requested
        if "docx" in result:
            docx_url = result["docx"]
            docx_content = self._download_url(docx_url, binary=True)
            docx_file = output_path / f"{base_name}.docx"
            docx_file.write_bytes(docx_content)
            logger.info(f"DOCX saved: {docx_file}")

        # Save metadata
        metadata_file = output_path / f"{base_name}_metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        logger.info(f"Metadata saved: {metadata_file}")

    def _download_url(self, url: str, binary: bool = False) -> Any:
        """Download content from a URL."""
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        if binary:
            return response.content
        return response.text

    def get_markdown_from_result(self, result: Dict[str, Any]) -> str:
        """
        Extract markdown content from conversion result.

        Args:
            result: Conversion result from parse_pdf()

        Returns:
            Markdown content as string
        """
        # Check if we have a direct markdown URL (old API format)
        if "md" in result and isinstance(result["md"], str):
            md_url = result["md"]
        # Otherwise, construct the URL from pdf_id (new API format)
        elif "pdf_id" in result:
            pdf_id = result["pdf_id"]
            # Verify the markdown conversion is complete
            conversion_status = result.get("conversion_status", {})
            md_status = conversion_status.get("md", {})
            if md_status.get("status") != "completed":
                raise ValueError(f"Markdown conversion not completed. Status: {md_status}")
            
            # Construct download URL: https://api.mathpix.com/v3/pdf/{pdf_id}.md
            md_url = f"{self.config.api_url}/{pdf_id}.md"
            logger.info(f"Constructed markdown URL: {md_url}")
        else:
            available_keys = list(result.keys())
            raise ValueError(f"Cannot find markdown URL or pdf_id in result. Available keys: {available_keys}")

        return self._download_url(md_url)

    def parse_pdf_to_markdown(
        self,
        pdf_path: str,
        page_range: Optional[str] = None,
        save_to_file: Optional[str] = None
    ) -> str:
        """
        Convenience method to parse PDF directly to markdown string.

        Args:
            pdf_path: Path to PDF file
            page_range: Optional page range (e.g., "1-50")
            save_to_file: Optional path to save markdown

        Returns:
            Markdown content as string
        """
        result = self.parse_pdf(
            pdf_path=pdf_path,
            page_range=page_range,
            conversion_formats={"md": True}
        )

        markdown = self.get_markdown_from_result(result)

        if save_to_file:
            save_path = Path(save_to_file)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.write_text(markdown, encoding="utf-8")
            logger.info(f"Markdown saved to: {save_path}")

        return markdown


def parse_textbook_pdf(
    pdf_path: str,
    output_markdown_path: str,
    page_range: Optional[str] = None
) -> str:
    """
    Convenience function to parse a textbook PDF to markdown.

    Args:
        pdf_path: Path to the PDF textbook
        output_markdown_path: Where to save the markdown output
        page_range: Optional page range (e.g., "1-100" for first 100 pages)

    Returns:
        Markdown content

    Example:
        markdown = parse_textbook_pdf(
            "textbook.pdf",
            "textbook.md",
            page_range="1-50"
        )
    """
    parser = MathpixPDFParser.from_env()
    return parser.parse_pdf_to_markdown(
        pdf_path=pdf_path,
        page_range=page_range,
        save_to_file=output_markdown_path
    )
