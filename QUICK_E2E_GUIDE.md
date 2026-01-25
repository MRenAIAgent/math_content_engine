# Quick E2E Testing Guide

**TL;DR:** The current system does **text→video**, not **image→OCR→analysis→video**.

---

## ✅ What Works Now (Verified 2026-01-23)

### Test 1: Generate Video from Text (1 minute)

```bash
# Activate environment
source venv/bin/activate

# Set API key
export ANTHROPIC_API_KEY=sk-ant-your-key

# Run example
python examples/basic_usage.py
```

**Expected Output:**
```
✅ Generated: ./output/pythagorean_theorem_xxxxx.mp4
```

### Test 2: Template-Based Generation (30 seconds)

```bash
python examples/template_usage.py
```

**Expected Output:**
```
✅ Generated: ./output/linear_equation.mp4
   Template: linear_equation_graph
   Parameters: {a: 3, b: 5, c: 14}
```

### Test 3: Run All Tests (1 minute)

```bash
# Unit tests (fast)
pytest tests/test_validators.py tests/test_code_extractor.py \
       tests/test_config.py tests/test_constants.py \
       tests/test_llm_clients.py -v

# Expected: ✅ 73/73 passed in ~0.5s

# Template tests
pytest tests/test_templates.py -v

# Expected: ✅ 34/34 passed
```

### Test 4: Start REST API (2 minutes)

```bash
# Terminal 1: Start server
math-api

# Terminal 2: Test endpoints
curl http://localhost:8000/api/v1/videos
curl http://localhost:8000/api/v1/videos/stats/summary
```

---

## ❌ What Doesn't Work (Not Implemented)

### Image-Based Workflow

The following does **NOT exist**:

```python
# ❌ This won't work - not implemented yet
from math_content_engine import ImageAnalysisEngine

engine = ImageAnalysisEngine()
result = engine.analyze_image("student_work.jpg")
# Would return: OCR text, errors, gaps, knowledge graph, video
```

**Why:** The system wasn't built for image input. It only handles text input.

---

## Current Capabilities

| Feature | Status | Test File |
|---------|--------|-----------|
| Text → Video (LLM) | ✅ Working | `test_integration.py` |
| Text → Video (Template) | ✅ Working | `test_templates.py` |
| TTS/Narration | ✅ Working | `test_voice_video_sync.py` |
| REST API | ✅ Working | `test_api.py` |
| Code Validation | ✅ Working | `test_validators.py` |
| **Image Upload** | ❌ Missing | N/A |
| **OCR** | ❌ Missing | N/A |
| **Error Detection** | ❌ Missing | N/A |
| **Gap Detection** | ❌ Missing | N/A |
| **Knowledge Graph** | ❌ Missing | N/A |

---

## Quick Verification Checklist

- [x] Clone repo
- [x] Install dependencies (`pip install -e .`)
- [x] Set API key in `.env`
- [x] Run basic example (`python examples/basic_usage.py`)
- [x] Run template example (`python examples/template_usage.py`)
- [x] Run tests (`pytest tests/`)
- [x] Start API server (`math-api`)
- [x] Test API endpoints (`curl ...`)
- [ ] ~~Upload image~~ (not implemented)
- [ ] ~~Run OCR~~ (not implemented)
- [ ] ~~Detect errors~~ (not implemented)

---

## Next Steps

**If you need the image-based workflow:**

1. Read `E2E_VERIFICATION_REPORT.md` for full details
2. Clarify requirements (OCR service, error types, etc.)
3. Choose implementation approach (extend current vs new service)
4. Estimate: 2-4 weeks for MVP

**If current system is sufficient:**

1. See `TEMPLATE_SYSTEM_EXPLAINED.md` for template usage
2. See `REFACTORING_SUMMARY.md` for architecture details
3. See `QUICK_START_REFACTORING.md` for enum migration

---

## Documentation Files

| File | Purpose |
|------|---------|
| `E2E_WORKFLOW_DOCUMENTATION.md` | Complete workflow documentation |
| `E2E_VERIFICATION_REPORT.md` | Detailed verification report |
| `QUICK_E2E_GUIDE.md` | This file - quick reference |
| `TEMPLATE_SYSTEM_EXPLAINED.md` | Template system guide |
| `REFACTORING_SUMMARY.md` | Architecture analysis |

---

**Questions?** Check the detailed reports above or let me know what you need!
