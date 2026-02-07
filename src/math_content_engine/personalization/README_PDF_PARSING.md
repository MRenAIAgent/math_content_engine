# PDF Parsing Module

This module provides PDF parsing capabilities using the Mathpix API, which specializes in extracting mathematical content from PDFs with high accuracy.

## Quick Start

```python
from math_content_engine.personalization import parse_textbook_pdf

# Parse PDF to markdown
markdown = parse_textbook_pdf(
    pdf_path="textbook.pdf",
    output_markdown_path="textbook.md",
    page_range="1-50"  # Optional: parse only specific pages
)
```

## Features

- ✅ **Mathematical OCR**: Excellent recognition of LaTeX equations
- ✅ **Table Extraction**: Preserves table structure
- ✅ **Page Ranges**: Parse specific chapters/sections
- ✅ **Multiple Formats**: Export to markdown, DOCX, LaTeX, HTML
- ✅ **Spell Checking**: Built-in spell correction
- ✅ **Table Fallback**: Alternative table parsing for complex layouts

## Installation

```bash
pip install -e ".[pdf]"
```

## Configuration

Set environment variables in `.env`:

```bash
MATHPIX_APP_ID=your_app_id
MATHPIX_APP_KEY=your_app_key
```

## API Reference

### Classes

#### `MathpixPDFParser`

Main parser class.

**Methods:**
- `from_env()` - Create parser from environment variables
- `parse_pdf(pdf_path, ...)` - Parse PDF and return result dict
- `parse_pdf_to_markdown(pdf_path, page_range, save_to_file)` - Direct markdown extraction
- `get_markdown_from_result(result)` - Extract markdown from result dict

#### `MathpixConfig`

Configuration dataclass.

**Attributes:**
- `app_id: str` - Mathpix app ID
- `app_key: str` - Mathpix app key
- `api_url: str` - API endpoint (default: https://api.mathpix.com/v3/pdf)
- `conversion_formats: Dict` - Output formats

### Functions

#### `parse_textbook_pdf(pdf_path, output_markdown_path, page_range=None)`

Convenience function for quick PDF to markdown conversion.

**Parameters:**
- `pdf_path`: Path to PDF file
- `output_markdown_path`: Where to save markdown
- `page_range`: Optional page range (e.g., "1-50", "10-", "-30")

**Returns:** Markdown content as string

## Usage Examples

### Basic Parsing

```python
from math_content_engine.personalization import MathpixPDFParser

# Initialize from environment
parser = MathpixPDFParser.from_env()

# Parse entire PDF
result = parser.parse_pdf("textbook.pdf")
markdown = parser.get_markdown_from_result(result)
```

### Parse Specific Pages

```python
# Parse only chapter 2 (pages 20-50)
result = parser.parse_pdf(
    pdf_path="textbook.pdf",
    page_range="20-50",
    output_dir="output/"
)
```

### Custom Configuration

```python
from math_content_engine.personalization import MathpixConfig, MathpixPDFParser

config = MathpixConfig(
    app_id="your_id",
    app_key="your_key",
    conversion_formats={
        "md": True,
        "docx": True,
        "latex_zip": False,
        "html": False
    }
)

parser = MathpixPDFParser(config)
result = parser.parse_pdf("textbook.pdf")
```

### Integration with Textbook Parser

```python
from math_content_engine.personalization import (
    parse_textbook_pdf,
    TextbookParser
)

# Step 1: Parse PDF to markdown
markdown_path = "textbook.md"
parse_textbook_pdf("textbook.pdf", markdown_path)

# Step 2: Parse markdown textbook structure
parser = TextbookParser(markdown_path)
chapter = parser.parse()

# Step 3: Get animation specs
animation_specs = parser.get_examples_for_animation()
```

## Page Range Syntax

| Format | Description | Example |
|--------|-------------|---------|
| `N-M` | Pages N through M | `"1-50"` |
| `N-` | Page N to end | `"10-"` |
| `-M` | Start to page M | `"-30"` |
| `N` | Single page | `"25"` |

## Error Handling

```python
from math_content_engine.personalization import MathpixPDFParser

parser = MathpixPDFParser.from_env()

try:
    result = parser.parse_pdf("textbook.pdf")
    markdown = parser.get_markdown_from_result(result)
except FileNotFoundError:
    print("PDF file not found")
except ValueError as e:
    print(f"Configuration error: {e}")
except TimeoutError:
    print("PDF conversion timed out")
except RuntimeError as e:
    print(f"Conversion failed: {e}")
```

## Advanced Options

### Enable Spell Checking

```python
result = parser.parse_pdf(
    pdf_path="textbook.pdf",
    enable_spell_check=True
)
```

### Table Extraction Fallback

```python
result = parser.parse_pdf(
    pdf_path="textbook.pdf",
    enable_tables_fallback=True  # Use alternative table parser
)
```

### Multiple Output Formats

```python
result = parser.parse_pdf(
    pdf_path="textbook.pdf",
    conversion_formats={
        "md": True,
        "docx": True,
        "html": True
    },
    output_dir="output/"
)

# Access different formats
markdown_url = result["md"]
docx_url = result["docx"]
html_url = result["html"]
```

## Cost Optimization

Mathpix is a paid API. Optimize usage:

1. **Parse once, use many times**
   ```python
   # Parse PDF once
   parse_textbook_pdf("textbook.pdf", "textbook.md")

   # Reuse markdown multiple times (no additional API calls)
   # For personalization, animation generation, etc.
   ```

2. **Use page ranges**
   ```python
   # Only parse needed chapters
   parse_textbook_pdf("textbook.pdf", "chapter2.md", page_range="20-50")
   ```

3. **Cache results**
   - Save parsed markdown files
   - Version control markdown outputs
   - Reuse across different interests/personalizations

## Limitations

- **API Rate Limits**: Check Mathpix dashboard for quotas
- **File Size**: Large PDFs may take several minutes
- **Quality**: OCR accuracy depends on PDF quality
- **Cost**: Usage-based pricing (check mathpix.com/pricing)

## Troubleshooting

### "Mathpix credentials not found"

Add credentials to `.env`:
```bash
MATHPIX_APP_ID=your_id
MATHPIX_APP_KEY=your_key
```

### Conversion Timeout

Increase timeout for large PDFs:
```python
result = parser._wait_for_conversion(
    pdf_id="...",
    max_wait_seconds=1200  # 20 minutes
)
```

### Poor OCR Quality

- Ensure PDF has good scan quality
- Try `enable_spell_check=True`
- Contact Mathpix support for difficult documents

## See Also

- [Full PDF Parsing Guide](../../../../docs/PDF_PARSING_GUIDE.md)
- [Mathpix API Documentation](https://docs.mathpix.com/)
- [TextbookParser](./textbook_parser.py) - Parse markdown textbooks
- [ContentPersonalizer](./personalizer.py) - Personalize content for students
