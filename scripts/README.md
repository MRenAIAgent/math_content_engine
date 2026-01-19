# Scripts

This directory contains utility scripts for various tasks related to the Math Content Engine.

## Personalization Scripts

### `personalized_content_pipeline.py`
**Purpose:** End-to-end pipeline for generating personalized math content based on student interests.

**Features:**
- Takes student interest profiles and generates customized learning materials
- Integrates with the personalization engine
- Produces animations tailored to individual learning preferences

**Usage:**
```bash
python scripts/personalized_content_pipeline.py
```

### `generate_personalized_textbook.py`
**Purpose:** Generates personalized textbook content from curriculum materials.

**Features:**
- Adapts textbook content to student interests
- Creates customized examples and explanations
- Maintains alignment with Common Core standards

**Usage:**
```bash
python scripts/generate_personalized_textbook.py
```

## Curriculum Scripts

Located in `scripts/curriculum/`, these scripts work with curriculum content generation.

### `curriculum/generate_personalized_chapter.py`
**Purpose:** Generates a personalized version of a specific curriculum chapter.

**Features:**
- Chapter-by-chapter personalization
- Interest-based adaptation of examples
- Algebra 1 curriculum support

**Usage:**
```bash
python scripts/curriculum/generate_personalized_chapter.py
```

### `curriculum/regenerate_chapter2_opus.py`
**Purpose:** Regenerates Chapter 2 content using Claude Opus model for higher quality.

**Features:**
- Uses Claude Opus for enhanced content generation
- Specific to Chapter 2 of Algebra 1 curriculum
- Produces higher-quality explanations and examples

**Usage:**
```bash
python scripts/curriculum/regenerate_chapter2_opus.py
```

## Development Notes

- All scripts assume the package is installed (`pip install -e .`)
- Scripts may require API keys (ANTHROPIC_API_KEY or OPENAI_API_KEY)
- See main README.md for environment setup
- Configure via environment variables or `.env` file
