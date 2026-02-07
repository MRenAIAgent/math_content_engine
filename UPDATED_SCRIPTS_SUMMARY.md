# Updated Scripts Summary

## Changes Made

### 1. ✅ Updated `personalized_content_pipeline.py`

**Location:** `scripts/personalized_content_pipeline.py`

**What Changed:**
- Added PDF parsing support at the beginning of the pipeline
- If `--pdf` is provided, it automatically parses to markdown first, then continues with personalization
- Added `--page-range` parameter for parsing specific PDF pages
- Added PDF-only mode with `--output-markdown` flag

**New Usage:**

```bash
# Full pipeline from PDF (new!)
python scripts/personalized_content_pipeline.py \
    --pdf textbook.pdf \
    --interest basketball \
    --output-dir output/ \
    --page-range "1-50"

# PDF to markdown only (new!)
python scripts/personalized_content_pipeline.py \
    --pdf textbook.pdf \
    --output-markdown textbook.md \
    --page-range "1-50"

# Original markdown workflow still works
python scripts/personalized_content_pipeline.py \
    --textbook textbook.md \
    --interest basketball \
    --output-dir output/
```

**Key Features:**
- ✅ Automatic PDF detection and parsing
- ✅ Seamless integration with existing pipeline
- ✅ Page range support
- ✅ PDF-only mode for checking parser results
- ✅ Backwards compatible with existing markdown workflow

---

### 2. ✅ Created New `parse_pdf.py` Script

**Location:** `scripts/parse_pdf.py`

**Purpose:** Simple standalone script to parse PDF → markdown for checking results

**Usage:**

```bash
# Parse entire PDF
python scripts/parse_pdf.py input.pdf output.md

# Parse specific pages
python scripts/parse_pdf.py input.pdf output.md --page-range "1-50"

# Verbose mode
python scripts/parse_pdf.py input.pdf output.md --verbose
```

**Features:**
- ✅ Simple command-line interface
- ✅ Shows preview of first 10 lines
- ✅ Reports character count and line count
- ✅ Verbose mode for debugging
- ✅ Clear error messages
- ✅ Perfect for checking parser quality before full pipeline

---

## Complete Workflow Examples

### Example 1: Check PDF Parser Quality First

```bash
# Step 1: Parse PDF to markdown and check quality
python scripts/parse_pdf.py \
    curriculum/textbooks/us/ca_common_core_algebra1.pdf \
    test_output.md \
    --page-range "1-10"

# Step 2: Review the markdown file
cat test_output.md | head -100

# Step 3: If quality is good, run full pipeline
python scripts/personalized_content_pipeline.py \
    --pdf curriculum/textbooks/us/ca_common_core_algebra1.pdf \
    --interest basketball \
    --output-dir output/basketball_algebra \
    --page-range "1-100"
```

### Example 2: One-Step Full Pipeline

```bash
# Parse PDF and generate personalized content in one command
python scripts/personalized_content_pipeline.py \
    --pdf textbook.pdf \
    --interest basketball gaming \
    --output-dir output/personalized \
    --page-range "1-50" \
    --max-examples 5
```

### Example 3: Save Parsed Markdown for Reuse

```bash
# Step 1: Parse PDF once (saves API cost)
python scripts/parse_pdf.py \
    textbook.pdf \
    textbook.md \
    --page-range "1-100"

# Step 2: Use parsed markdown multiple times
python scripts/personalized_content_pipeline.py \
    --textbook textbook.md \
    --interest basketball \
    --output-dir output/basketball

python scripts/personalized_content_pipeline.py \
    --textbook textbook.md \
    --interest gaming \
    --output-dir output/gaming
```

---

## Command Reference

### `personalized_content_pipeline.py`

**PDF Input (New):**
```bash
python scripts/personalized_content_pipeline.py \
    --pdf <pdf_file> \
    --interest <interest1> [<interest2> ...] \
    --output-dir <output_directory> \
    [--page-range "N-M"] \
    [--max-examples N] \
    [--preview]
```

**PDF to Markdown Only (New):**
```bash
python scripts/personalized_content_pipeline.py \
    --pdf <pdf_file> \
    --output-markdown <output_md_file> \
    [--page-range "N-M"]
```

**Markdown Input (Original):**
```bash
python scripts/personalized_content_pipeline.py \
    --textbook <markdown_file> \
    --interest <interest1> [<interest2> ...] \
    --output-dir <output_directory> \
    [--max-examples N] \
    [--preview]
```

### `parse_pdf.py`

**Simple PDF Parsing:**
```bash
python scripts/parse_pdf.py <input.pdf> <output.md> [--page-range "N-M"] [--verbose]
```

---

## Page Range Syntax

Both scripts support the same page range format:

| Format | Description | Example |
|--------|-------------|---------|
| `N-M` | Pages N through M | `"1-50"` = pages 1-50 |
| `N-` | Page N to end | `"10-"` = page 10 to end |
| `-M` | Start to page M | `"-30"` = start to page 30 |
| `N` | Single page N | `"25"` = only page 25 |

---

## Quick Start Guide

### 1. Setup (One Time)

```bash
# Install dependencies
pip install -e ".[pdf]"

# Add to .env file
echo "MATHPIX_APP_ID=your_app_id" >> .env
echo "MATHPIX_APP_KEY=your_app_key" >> .env
```

### 2. Test PDF Parser

```bash
# Parse a few pages to test
python scripts/parse_pdf.py \
    curriculum/textbooks/us/ca_common_core_algebra1.pdf \
    test.md \
    --page-range "1-5" \
    --verbose

# Check the output
cat test.md
```

### 3. Run Full Pipeline

```bash
# Generate basketball-themed algebra content
python scripts/personalized_content_pipeline.py \
    --pdf curriculum/textbooks/us/ca_common_core_algebra1.pdf \
    --interest basketball \
    --output-dir output/basketball_algebra \
    --page-range "1-50" \
    --max-examples 10
```

---

## Benefits of This Approach

### ✅ Flexibility
- Use PDF input directly
- Or use markdown if you already have it
- Or check PDF quality first with `parse_pdf.py`

### ✅ Cost Optimization
- Parse PDF once with `parse_pdf.py`
- Reuse markdown for multiple interests
- Avoid redundant Mathpix API calls

### ✅ Quality Control
- Check parser output before full pipeline
- Adjust page ranges if needed
- Verify LaTeX equations are correct

### ✅ Backwards Compatible
- Original markdown workflow still works
- No breaking changes to existing scripts
- All previous examples still work

---

## File Summary

| File | Purpose | Status |
|------|---------|--------|
| `scripts/personalized_content_pipeline.py` | Main pipeline (updated) | ✅ Updated |
| `scripts/parse_pdf.py` | Simple PDF parser (new) | ✅ New |

**Note:** All functionality is consolidated into these two scripts:
- `personalized_content_pipeline.py` - Full pipeline with PDF support
- `parse_pdf.py` - Standalone parser for quality checks

---

## Scripts Overview

### Main Pipeline Script
`scripts/personalized_content_pipeline.py` handles all workflows:
- PDF → personalized textbook → animations
- Markdown → personalized textbook → animations
- Existing personalized textbook → animations

### Simple Parser Script
`scripts/parse_pdf.py` for quick PDF testing:
- PDF → markdown only
- Shows preview and statistics
- Perfect for checking parser quality
