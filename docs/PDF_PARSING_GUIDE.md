# PDF Parsing Guide

This guide explains how to use the Mathpix PDF parser to extract mathematical content from PDF textbooks.

---

## Overview

The Math Content Engine now supports parsing PDF textbooks using the **Mathpix API**, which provides excellent OCR for mathematical equations, tables, and complex notation.

### Capabilities

- ✅ Extract text and LaTeX equations from PDFs
- ✅ Preserve mathematical notation and formatting
- ✅ Convert to clean markdown format
- ✅ Handle tables and complex layouts
- ✅ Process specific page ranges
- ✅ Integration with personalization pipeline

---

## Setup

### 1. Get Mathpix API Credentials

1. Sign up at [mathpix.com](https://mathpix.com/)
2. Navigate to your dashboard
3. Create a new API key
4. Note your `APP_ID` and `APP_KEY`

### 2. Configure Environment Variables

Add to your `.env` file:

```bash
# Mathpix API credentials
MATHPIX_APP_ID=your_app_id_here
MATHPIX_APP_KEY=your_app_key_here
```

### 3. Install Dependencies

```bash
# Install with PDF support
pip install -e ".[pdf]"

# Or install all features
pip install -e ".[all]"
```

This installs:
- `mathpix>=0.1.0` - Mathpix Python SDK
- `requests>=2.31.0` - HTTP client

---

## Usage

### Option 1: Python API

#### Basic PDF Parsing

```python
from math_content_engine.personalization import parse_textbook_pdf

# Parse entire PDF to markdown
markdown = parse_textbook_pdf(
    pdf_path="curriculum/textbooks/us/openstax_elementary_algebra_2e.pdf",
    output_markdown_path="output/textbook.md"
)

print(markdown)
```

#### Parse Specific Pages

```python
from math_content_engine.personalization import MathpixPDFParser

# Parse only pages 1-50
parser = MathpixPDFParser.from_env()
result = parser.parse_pdf(
    pdf_path="textbook.pdf",
    page_range="1-50",
    output_dir="output/"
)

# Get markdown content
markdown = parser.get_markdown_from_result(result)
```

#### Advanced Configuration

```python
from math_content_engine.personalization import MathpixPDFParser, MathpixConfig

# Custom configuration
config = MathpixConfig(
    app_id="your_app_id",
    app_key="your_app_key",
    conversion_formats={
        "md": True,      # Markdown
        "docx": True,    # MS Word
        "latex_zip": False,
        "html": False
    }
)

parser = MathpixPDFParser(config)
result = parser.parse_pdf(
    pdf_path="textbook.pdf",
    output_dir="output/",
    enable_tables_fallback=True,
    enable_spell_check=True
)
```

### Option 2: Command-Line Script

#### PDF to Markdown Only

```bash
# Convert entire PDF
python scripts/pdf_to_personalized_pipeline.py \
    --pdf curriculum/textbooks/us/openstax_elementary_algebra_2e.pdf \
    --output-markdown output/algebra.md

# Convert specific pages
python scripts/pdf_to_personalized_pipeline.py \
    --pdf textbook.pdf \
    --output-markdown output/chapter2.md \
    --page-range "20-50"
```

#### Full Pipeline: PDF → Personalization → Animations

```bash
# Parse PDF and generate personalized content
python scripts/pdf_to_personalized_pipeline.py \
    --pdf curriculum/textbooks/us/openstax_elementary_algebra_2e.pdf \
    --interest basketball gaming \
    --output-dir output/personalized_algebra \
    --page-range "1-100" \
    --max-examples 10
```

#### Preview Mode (Code Only, No Rendering)

```bash
python scripts/pdf_to_personalized_pipeline.py \
    --pdf textbook.pdf \
    --interest basketball \
    --output-dir output/ \
    --preview \
    --page-range "1-20"
```

---

## Page Range Syntax

The `--page-range` parameter supports various formats:

| Format | Description | Example |
|--------|-------------|---------|
| `N-M` | Pages N through M | `"1-50"` = pages 1 to 50 |
| `N-` | Page N to end | `"10-"` = page 10 to end |
| `-M` | Start to page M | `"-30"` = start to page 30 |
| `N` | Single page N | `"25"` = only page 25 |

---

## Complete Workflow Examples

### Example 1: Basketball-Themed Algebra Textbook

```bash
# Step 1: Parse PDF (pages 1-100)
python scripts/pdf_to_personalized_pipeline.py \
    --pdf curriculum/textbooks/us/openstax_elementary_algebra_2e.pdf \
    --page-range "1-100" \
    --interest basketball \
    --output-dir output/basketball_algebra \
    --max-examples 5

# Output:
# - output/basketball_algebra/openstax_elementary_algebra_2e.md (parsed PDF)
# - output/basketball_algebra/basketball/textbook_basketball.md (personalized)
# - output/basketball_algebra/basketball/videos/*.mp4 (animations)
```

### Example 2: Multiple Interests from Single PDF

```bash
python scripts/pdf_to_personalized_pipeline.py \
    --pdf textbook.pdf \
    --interest basketball gaming music anime \
    --output-dir output/multi_interest \
    --page-range "1-50" \
    --preview  # Generate code only, no rendering
```

### Example 3: Use Existing Markdown

```bash
# If you already have markdown from previous PDF parsing
python scripts/pdf_to_personalized_pipeline.py \
    --markdown output/textbook.md \
    --interest soccer \
    --output-dir output/soccer_textbook
```

---

## Integration with Existing Pipeline

The PDF parser integrates seamlessly with the existing personalization pipeline:

```python
from pathlib import Path
from math_content_engine import MathContentEngine, Config
from math_content_engine.personalization import (
    parse_textbook_pdf,
    TextbookParser,
)

# 1. Parse PDF to markdown
markdown_path = "output/textbook.md"
parse_textbook_pdf("textbook.pdf", markdown_path, page_range="1-50")

# 2. Parse markdown textbook
parser = TextbookParser(markdown_path)
chapter = parser.parse()
animation_specs = parser.get_examples_for_animation()

# 3. Generate animations
config = Config.from_env()
engine = MathContentEngine(config, interest="basketball")

for spec in animation_specs[:5]:  # First 5 examples
    result = engine.generate(
        topic=spec['topic'],
        requirements=spec['requirements'],
        output_filename=f"example_{spec['example_num']}"
    )
    print(f"Video: {result.video_path}")
```

---

## API Reference

### `MathpixPDFParser`

Main class for PDF parsing.

#### Methods

**`__init__(config: MathpixConfig)`**
- Initialize parser with configuration

**`from_env() -> MathpixPDFParser`**
- Create parser from environment variables
- Requires `MATHPIX_APP_ID` and `MATHPIX_APP_KEY`

**`parse_pdf(pdf_path, output_dir=None, page_range=None, ...) -> Dict`**
- Parse PDF and return conversion result
- Returns dict with markdown URL and metadata

**`parse_pdf_to_markdown(pdf_path, page_range=None, save_to_file=None) -> str`**
- Convenience method to get markdown directly
- Returns markdown as string

**`get_markdown_from_result(result: Dict) -> str`**
- Extract markdown content from parse result

### `MathpixConfig`

Configuration dataclass.

#### Attributes

- `app_id: str` - Mathpix app ID
- `app_key: str` - Mathpix app key
- `api_url: str` - API endpoint (default: `https://api.mathpix.com/v3/pdf`)
- `conversion_formats: Dict` - Output formats to generate

#### Methods

**`from_env() -> MathpixConfig`**
- Load configuration from environment variables

### Convenience Functions

**`parse_textbook_pdf(pdf_path, output_markdown_path, page_range=None) -> str`**
- Simple function to parse PDF to markdown file
- Returns markdown content

---

## Cost Considerations

Mathpix API is a paid service with usage-based pricing:

- **Free tier**: Limited pages per month
- **Paid plans**: Per-page pricing

### Tips to Minimize Costs

1. **Use page ranges**: Only parse chapters you need
   ```bash
   --page-range "20-50"  # Only chapter 2
   ```

2. **Cache results**: Save parsed markdown files for reuse
   ```bash
   # Parse once
   python scripts/pdf_to_personalized_pipeline.py \
       --pdf textbook.pdf \
       --output-markdown textbook.md

   # Reuse markdown multiple times
   python scripts/pdf_to_personalized_pipeline.py \
       --markdown textbook.md \
       --interest basketball \
       --output-dir output/
   ```

3. **Process in batches**: Parse full textbook once, then personalize multiple times

---

## Troubleshooting

### Error: "Mathpix credentials not found"

**Solution**: Add credentials to `.env` file:
```bash
MATHPIX_APP_ID=your_app_id
MATHPIX_APP_KEY=your_app_key
```

### Error: "PDF conversion failed"

**Possible causes**:
- Invalid PDF file
- Corrupted PDF
- API quota exceeded
- Network issues

**Solution**: Check Mathpix dashboard for error details

### Timeout Errors

**Solution**: Increase timeout for large PDFs:
```python
parser = MathpixPDFParser.from_env()
result = parser._wait_for_conversion(
    pdf_id="...",
    max_wait_seconds=1200  # 20 minutes
)
```

### Poor OCR Quality

**Solutions**:
- Ensure PDF has good quality scans
- Try adjusting conversion options
- Use `enable_spell_check=True`
- Contact Mathpix support for difficult documents

---

## Best Practices

### 1. Start Small

Test with a few pages first:
```bash
python scripts/pdf_to_personalized_pipeline.py \
    --pdf textbook.pdf \
    --page-range "1-10" \
    --output-markdown test.md
```

### 2. Cache Parsed Content

Always save markdown files for reuse:
```python
# Parse once
markdown = parse_textbook_pdf("textbook.pdf", "textbook.md")

# Use many times for different interests
# (no additional Mathpix API calls)
```

### 3. Validate Output

Check the parsed markdown before using in pipeline:
```bash
# View parsed content
cat output/textbook.md | head -100

# Check for equation quality
grep '\$' output/textbook.md
```

### 4. Use Preview Mode

Test animations without rendering videos first:
```bash
--preview --max-examples 3
```

---

## See Also

- [Mathpix API Documentation](https://docs.mathpix.com/)
- [Personalization Guide](../curriculum/algebra1/textbooks/README.md)
- [Animation Pipeline](../scripts/personalized_content_pipeline.py)
- [CLAUDE.md](../CLAUDE.md) - Build and development guide
