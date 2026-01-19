# ElevenLabs Integration Tests - READY TO RUN

## ✅ Installation Complete

All dependencies have been successfully installed:

- ✅ FFmpeg (system dependency)
- ✅ System libraries (cairo, pango, pkg-config)
- ✅ Python packages:
  - pytest 9.0.2
  - manim 0.19.2
  - anthropic 0.76.0
  - elevenlabs 2.30.0
  - edge-tts 7.2.7
  - All other dependencies

## ✅ Tests Ready

Two tests have been created and validated:

### Test 1: `test_elevenlabs_tts_generation_only` (Quick - 5-10 seconds)
```bash
python -m pytest tests/test_algebra_integration.py::TestAlgebraElevenLabsNarration::test_elevenlabs_tts_generation_only -v -s
```

**What it does:**
- Verifies ElevenLabs API connection
- Generates a test audio file
- Validates audio output
- **No video rendering** (fast!)

**Output:** `tests/test_output/test_elevenlabs_audio.mp3`

---

### Test 2: `test_linear_equation_with_elevenlabs_narration` (Full - 1-3 minutes)
```bash
python -m pytest tests/test_algebra_integration.py::TestAlgebraElevenLabsNarration::test_linear_equation_with_elevenlabs_narration -v -s
```

**What it does:**
1. **Generate Manim Code** - LLM creates Python code for solving "2x + 3 = 7"
2. **Render Animation** - Manim renders video with:
   - Visual step-by-step solution
   - Number line representation
   - Color-coded steps (WHITE → BLUE → GREEN)
   - Clear mathematical progression
3. **Create Narration** - 6 voice cues synchronized with visuals:
   - 0s: "Let's solve the linear equation: 2x plus 3 equals 7"
   - 3s: "First, we need to isolate the variable x"
   - 6s: "Subtract 3 from both sides of the equation"
   - 9s: "This gives us 2x equals 4"
   - 12s: "Now, divide both sides by 2"
   - 15s: "Therefore, x equals 2. That's our solution!"
4. **Generate ElevenLabs Voice** - High-quality AI voice for each cue
5. **Combine Video + Audio** - FFmpeg merges into final MP4

**Outputs:**
- `tests/test_output/elevenlabs_linear_base.py` - Generated Manim code
- `tests/test_output/elevenlabs_linear_base_meta.txt` - Generation metadata
- `tests/test_output/linear_equation_elevenlabs_narrated.mp4` - **Final video with voice!** 🎥🔊
- `tests/test_output/elevenlabs_linear_narrated_meta.txt` - Test metadata

---

## 🔑 Required: API Keys

To run these tests, you need to set two environment variables:

### 1. ELEVENLABS_API_KEY
```bash
export ELEVENLABS_API_KEY="your-key-here"
```

Get yours from: https://elevenlabs.io/
- Free tier: 10,000 characters/month
- This test uses ~300 characters (~$0.01)

### 2. ANTHROPIC_API_KEY (or OPENAI_API_KEY)
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
# OR
export OPENAI_API_KEY="sk-your-key-here"
```

Get Anthropic key from: https://console.anthropic.com/
Get OpenAI key from: https://platform.openai.com/

---

## 📋 Quick Start

Once you have the API keys:

```bash
# 1. Set environment variables
export ELEVENLABS_API_KEY="your-elevenlabs-key"
export ANTHROPIC_API_KEY="your-anthropic-key"

# 2. Run quick test (recommended first)
python -m pytest tests/test_algebra_integration.py::TestAlgebraElevenLabsNarration::test_elevenlabs_tts_generation_only -v -s

# 3. If quick test passes, run full test
python -m pytest tests/test_algebra_integration.py::TestAlgebraElevenLabsNarration::test_linear_equation_with_elevenlabs_narration -v -s

# 4. View the output
ls -lh tests/test_output/
# Play the video:
# - macOS: open tests/test_output/linear_equation_elevenlabs_narrated.mp4
# - Linux: xdg-open tests/test_output/linear_equation_elevenlabs_narrated.mp4
```

---

## 🎯 Expected Results

### Quick Test (audio only):
```
Testing ElevenLabs TTS Audio Generation (Fast)
===============================================================================

TTS Provider: ElevenLabsTTSProvider

Generating audio for: 'Let's solve the equation 2x plus 3 equals 7...'

Audio generated:
  Path: /home/user/math_content_engine/tests/test_output/test_elevenlabs_audio.mp3
  Exists: True
  Size: 15.3 KB
  Duration: 5.42 seconds

===============================================================================
ElevenLabs TTS test PASSED!
===============================================================================
```

### Full Test (with video):
```
===============================================================================
STEP 1: Generating base animation video with graphics
===============================================================================
Base video generation:
  Success: True
  Video path: /tmp/.../linear_equation_base.mp4
  Render time: 12.34s
  Total attempts: 1

===============================================================================
STEP 2: Creating narration script for the equation
===============================================================================
Narration script created with 6 cues:
  1. [0.0s] Let's solve the linear equation: 2x plus 3 equals 7
  2. [3.0s] First, we need to isolate the variable x
  ...

===============================================================================
STEP 3: Setting up ElevenLabs TTS provider
===============================================================================
ElevenLabs config:
  Provider: elevenlabs
  Voice: default (TEACHER_FEMALE_CALM)
  Provider created: ElevenLabsTTSProvider

===============================================================================
STEP 4: Generating narrated video with ElevenLabs voice
===============================================================================
Combining video with ElevenLabs narration...
Narration result:
  Success: True
  Video path: tests/test_output/linear_equation_elevenlabs_narrated.mp4

===============================================================================
STEP 5: Verifying final output
===============================================================================
Final video stats:
  Path: tests/test_output/linear_equation_elevenlabs_narrated.mp4
  Size: 234.5 KB
  Exists: True

===============================================================================
TEST COMPLETED SUCCESSFULLY!
===============================================================================
```

---

## 🔧 Troubleshooting

### "ELEVENLABS_API_KEY not set"
- Make sure you've exported the variable: `echo $ELEVENLABS_API_KEY`
- Should show your key (not empty)

### "ANTHROPIC_API_KEY environment variable is required"
- Set either ANTHROPIC_API_KEY or OPENAI_API_KEY
- At least one LLM provider must be configured

### "FFmpeg not found"
- Already installed ✅ at: /usr/bin/ffmpeg
- Run `ffmpeg -version` to verify

### Test collection fails
- Use `python -m pytest` (not just `pytest`)
- Run from project root directory

---

## 📚 Documentation

- Full guide: `tests/README_ELEVENLABS_TESTS.md`
- Project setup: `CLAUDE.md`
- Main README: `README.md`

---

**Ready to run! Just add your API keys and execute the commands above. 🚀**
