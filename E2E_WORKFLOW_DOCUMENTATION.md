# End-to-End Workflow Documentation

## Current System Status

**Last Verified:** 2026-01-23
**System Version:** 0.1.0
**Test Status:** ✅ 107/107 tests passing

---

## Existing E2E Flow (Text-to-Video)

### Overview
The current system implements a **text-to-video** pipeline that generates math animations from text descriptions.

### Flow Diagram
```
User Input (Text)
    ↓
┌─────────────────────────────────────┐
│ 1. Input Processing                 │
│    - Topic description               │
│    - Requirements (optional)         │
│    - Audience level                  │
│    - Style preferences               │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ 2. Code Generation                  │
│    - LLM generates Manim code        │
│    - OR Template-based generation    │
│    - Extract scene class name        │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ 3. Code Validation                  │
│    - Syntax check                    │
│    - Manim imports present           │
│    - Scene class exists              │
│    - construct() method present      │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ 4. Rendering (Manim)                │
│    - Execute Manim subprocess        │
│    - Generate MP4/GIF/MOV            │
│    - Handle errors (retry if needed) │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ 5. Optional: TTS/Narration          │
│    - Generate voice narration        │
│    - Sync audio with video           │
│    - Combine into final video        │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ 6. Storage & API                    │
│    - Store metadata in SQLite        │
│    - Save video file                 │
│    - Make available via REST API     │
└────────────────┬────────────────────┘
                 ↓
        Output: Video File + Metadata
```

### Implementation Status

#### ✅ Implemented Features

**1. Text-to-Video Generation**
- **File:** `src/math_content_engine/engine.py`
- **Class:** `MathContentEngine`
- **Methods:**
  - `generate(topic, requirements, audience_level, interest)` - Main entry point
  - Automatic retry on errors (up to 5 attempts)
  - Error feedback loop to LLM for fixing

**2. Template-Based Generation**
- **File:** `src/math_content_engine/templates/engine.py`
- **Class:** `TemplateEngine`
- **Features:**
  - Parameterized templates (no LLM needed)
  - Question parsing (regex or LLM)
  - Instant code generation
  - Example: "Solve 3x + 5 = 14" → video

**3. Code Validation**
- **File:** `src/math_content_engine/utils/validators.py`
- **Function:** `validate_manim_code(code)`
- **Checks:**
  - Python syntax
  - Manim imports
  - Scene class inheritance
  - construct() method
  - No dangerous code (input(), eval())

**4. Rendering**
- **File:** `src/math_content_engine/renderer/manim_renderer.py`
- **Class:** `ManimRenderer`
- **Features:**
  - Quality presets (480p to 4K)
  - Subprocess execution with timeout
  - Output path management
  - Error capture and reporting

**5. TTS/Narration (Optional)**
- **Directory:** `src/math_content_engine/tts/`
- **Providers:**
  - Edge TTS (free)
  - ElevenLabs (premium)
- **Features:**
  - Voice narration generation
  - Audio-video synchronization
  - Multiple voice options

**6. REST API**
- **File:** `src/math_content_engine/api/routes.py`
- **Endpoints:**
  - `GET /api/v1/videos` - List videos
  - `GET /api/v1/videos/{id}` - Get metadata
  - `GET /api/v1/videos/{id}/file` - Download video
  - `GET /api/v1/videos/{id}/code` - Get Manim code
  - `POST /api/v1/videos` - Create record
  - `DELETE /api/v1/videos/{id}` - Delete record
  - `GET /api/v1/videos/stats/summary` - Get statistics

**7. Storage**
- **File:** `src/math_content_engine/api/storage.py`
- **Class:** `VideoStorage`
- **Database:** SQLite
- **Schema:**
  - Video metadata
  - Generation parameters
  - LLM usage statistics
  - Render metrics

---

## Testing the Current E2E Flow

### Prerequisites
```bash
# Ensure environment is set up
source venv/bin/activate

# Set API key
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# Or copy .env.example to .env and edit
cp .env.example .env
```

### Test 1: Basic Text-to-Video
```python
from math_content_engine import MathContentEngine

# Initialize engine
engine = MathContentEngine()

# Generate video from text
result = engine.generate(
    topic="Pythagorean theorem",
    requirements="Show visual proof with squares",
    audience_level="high school"
)

if result.success:
    print(f"✅ Video: {result.video_path}")
    print(f"   Scene: {result.scene_name}")
    print(f"   Attempts: {result.attempts}")
else:
    print(f"❌ Error: {result.error_message}")
```

**Expected Output:**
```
✅ Video: ./output/pythagorean_theorem_xxxx.mp4
   Scene: PythagoreanTheoremScene
   Attempts: 1
```

### Test 2: Template-Based Generation
```python
from math_content_engine.templates.engine import TemplateEngine

# Initialize template engine
engine = TemplateEngine(use_simple_parser=True)

# Generate from question (no LLM needed!)
result = engine.generate_from_question(
    question="Solve 3x + 5 = 14",
    output_filename="linear_equation"
)

if result.success:
    print(f"✅ Video: {result.video_path}")
    print(f"   Template: {result.template_id}")
    print(f"   Parameters: {result.parameters}")
else:
    print(f"❌ Error: {result.error_message}")
```

**Expected Output:**
```
✅ Video: ./output/linear_equation.mp4
   Template: linear_equation_graph
   Parameters: {'a': 3, 'b': 5, 'c': 14, 'solution': 3}
```

### Test 3: With Narration
```python
from math_content_engine import MathContentEngine
from math_content_engine.config import Config, TTSProvider

# Configure with TTS
config = Config()
config.tts_provider = TTSProvider.EDGE  # Free TTS

engine = MathContentEngine(config)

# Generate with narration
from math_content_engine.tts import NarratedAnimationEngine

narrated_engine = NarratedAnimationEngine(config)
result = narrated_engine.generate_narrated(
    topic="Quadratic formula",
    requirements="Step-by-step explanation"
)

if result.success:
    print(f"✅ Video with narration: {result.video_path}")
else:
    print(f"❌ Error: {result.error_message}")
```

### Test 4: REST API
```bash
# Start the API server
math-api

# In another terminal, test endpoints:

# List all videos
curl http://localhost:8000/api/v1/videos

# Get specific video metadata
curl http://localhost:8000/api/v1/videos/{video_id}

# Download video file
curl http://localhost:8000/api/v1/videos/{video_id}/file -o video.mp4

# Get video code
curl http://localhost:8000/api/v1/videos/{video_id}/code

# Get statistics
curl http://localhost:8000/api/v1/videos/stats/summary
```

### Test 5: Run Automated Tests
```bash
# Unit tests (no dependencies)
pytest tests/test_validators.py tests/test_code_extractor.py tests/test_config.py -v

# Template tests
pytest tests/test_templates.py -v

# Integration tests (requires API key, but uses mocks)
pytest tests/test_integration.py -v

# E2E tests (requires API key + Manim)
pytest tests/test_algebra_integration.py -v --slow
```

---

## ❌ NOT YET IMPLEMENTED: Image-Based E2E Flow

### What You're Asking For (Not Yet Built)

The following workflow **does NOT exist** in the current system:

```
Image Upload
    ↓
OCR (Extract math problem from image)
    ↓
Error Detection (Find mistakes in student work)
    ↓
Gap Detection (Identify knowledge gaps)
    ↓
Knowledge Graph Analysis (Map prerequisite concepts)
    ↓
Generate Video (Explain concept) + Text Response
```

### Why This Doesn't Exist

The current system was designed for:
- **Input:** Text descriptions
- **Output:** Educational videos

The image-based workflow would require:
- **OCR Engine** - Not implemented
- **Error Detection** - Not implemented
- **Gap Analysis** - Not implemented
- **Knowledge Graph** - Not implemented
- **Image Upload Endpoint** - Not implemented

### Would You Like Me To...

**Option A:** Document the **existing** text-to-video flow in detail

**Option B:** Design and implement the **new** image-based workflow you need

**Option C:** Create a **hybrid** system that extends the current system with image analysis

---

## Current System Capabilities Summary

### ✅ What Works Now

1. **Text Input → Video Output**
   - LLM-generated animations
   - Template-based animations
   - Multiple quality levels
   - Error recovery

2. **Template System**
   - 10+ pre-built templates
   - Linear equations, graphing, quadratics
   - Instant generation (no LLM needed)

3. **TTS/Narration**
   - Voice-over generation
   - Audio-video sync
   - Multiple voice options

4. **REST API**
   - Video storage
   - Metadata retrieval
   - File download

5. **Testing**
   - 107 tests passing
   - Unit, integration, E2E coverage

### ❌ What's Missing (For Image-Based Workflow)

1. **Image Processing**
   - OCR capability
   - Handwriting recognition
   - Math symbol detection

2. **Analysis Features**
   - Error detection in student work
   - Gap analysis
   - Knowledge graph construction

3. **API Endpoints**
   - Image upload
   - OCR processing
   - Analysis results

4. **Database Schema**
   - Store image data
   - Store analysis results
   - Link errors to knowledge gaps

---

## Next Steps

**To verify the existing system:**
```bash
# Run all tests
pytest tests/ -v

# Should see: 107 passed
```

**To implement image-based workflow:**
1. Clarify requirements
2. Design API endpoints
3. Choose OCR provider
4. Implement error detection logic
5. Build knowledge graph
6. Integrate with video generation

---

## Questions for Clarification

Before I implement the image-based workflow, please clarify:

1. **OCR Requirements:**
   - Printed math problems or handwritten?
   - What OCR service to use? (Tesseract, Google Vision, AWS Textract?)
   - Languages to support?

2. **Error Detection:**
   - What types of errors? (Calculation, conceptual, procedural?)
   - How to detect them? (Rule-based or ML-based?)

3. **Gap Detection:**
   - What defines a "knowledge gap"?
   - How to map to prerequisites?

4. **Knowledge Graph:**
   - What graph database? (Neo4j, in-memory, JSON?)
   - How to build the graph?

5. **Integration:**
   - Should this extend the current system or be separate?
   - API-first or library-first?

Let me know which direction you'd like to go!
