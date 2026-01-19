# Voice-Video Synchronization Validation Guide

This guide explains how to verify that voice narration and video content are properly synchronized and consistent in educational videos.

## Table of Contents

1. [Automated Validation](#automated-validation)
2. [Manual Review Methods](#manual-review-methods)
3. [Tools and Utilities](#tools-and-utilities)
4. [Common Issues and Fixes](#common-issues-and-fixes)
5. [Best Practices](#best-practices)

---

## Automated Validation

### Built-in Test Validation

The ElevenLabs integration test automatically performs 6 synchronization checks:

```bash
pytest tests/test_algebra_integration.py::TestAlgebraElevenLabsNarration::test_linear_equation_with_elevenlabs_narration -v -s
```

**What it validates:**

1. ✅ **Audio Track Presence** - Confirms video has an audio track
2. ✅ **Duration Alignment** - Checks audio and video lengths match (within tolerance)
3. ✅ **Narration Timing** - Validates all voice cues fall within video duration
4. ✅ **Pacing Check** - Ensures gaps between narration aren't too fast/slow
5. ✅ **Content Consistency** - Verifies narration covers expected topics
6. ✅ **Subtitle Generation** - Creates SRT file for manual review

### Using the Sync Validator Standalone

```python
from test_voice_video_sync import VideoAudioSyncValidator

# Create validator
validator = VideoAudioSyncValidator(video_path)

# Check 1: Audio presence
has_audio = validator.check_audio_presence()
print(f"Audio track: {has_audio}")

# Check 2: Duration alignment
is_aligned, message = validator.check_sync_alignment(tolerance_seconds=1.0)
print(message)

# Check 3: Validate narration timing
narration_cues = [
    (0.0, "Introduction text"),
    (3.0, "Step 1 text"),
    (6.0, "Step 2 text"),
]
issues = validator.validate_narration_timing(narration_cues)
for issue in issues:
    print(issue)

# Check 4: Generate subtitles
srt_file = validator.generate_subtitle_file(narration_cues)
print(f"Subtitles saved to: {srt_file}")
```

### Command-Line Validation

```bash
# Quick validation of any video
python tests/test_voice_video_sync.py tests/test_output/linear_equation_elevenlabs_narrated.mp4
```

**Output:**
```
================================================================================
VIDEO-AUDIO SYNCHRONIZATION VALIDATION
================================================================================

Video: linear_equation_elevenlabs_narrated.mp4

1. Audio track present: True
2. Video duration: 16.24s
3. Audio duration: 16.18s

4. Sync check: ✅ Sync OK: video=16.24s, audio=16.18s, diff=0.06s

5. Narration timing validation:
   ✅ All 6 cues within video duration (16.24s)

6. Narration pacing check:
   ✅ Narration pacing is good (gaps between 2.0s and 8.0s)

7. Generating subtitle file for manual review...
   ✅ Subtitles saved to: linear_equation_elevenlabs_narrated_subs.srt
```

---

## Manual Review Methods

### Method 1: Play Video with Subtitles

The test automatically generates an SRT subtitle file. Load this in your video player to see narration timing:

**VLC Player:**
```bash
vlc tests/test_output/linear_equation_elevenlabs_narrated.mp4 \
    --sub-file=tests/test_output/linear_equation_elevenlabs_narrated_subs.srt
```

**mpv:**
```bash
mpv tests/test_output/linear_equation_elevenlabs_narrated.mp4 \
    --sub-file=tests/test_output/linear_equation_elevenlabs_narrated_subs.srt
```

**What to check:**
- Do subtitles appear when voice speaks?
- Does subtitle text match what's shown visually?
- Are timing transitions smooth?

### Method 2: Side-by-Side Comparison

Open the metadata file to see narration script alongside timing:

```bash
cat tests/test_output/elevenlabs_linear_narrated_meta.txt
```

**Example metadata:**
```
Narration Script:
  1. [0.0s] Let's solve the linear equation: 2x plus 3 equals 7
  2. [3.0s] First, we need to isolate the variable x
  3. [6.0s] Subtract 3 from both sides of the equation
  4. [9.0s] This gives us 2x equals 4
  5. [12.0s] Now, divide both sides by 2
  6. [15.0s] Therefore, x equals 2. That's our solution!

Synchronization Validation:
  Audio Track Present: True
  ✅ Sync OK: video=16.24s, audio=16.18s, diff=0.06s
  Timing Issues: 0
  Pacing Issues: 0
  Content Consistency: ✅ All topics covered
```

**What to check:**
- Play video and pause at each timestamp
- Verify visual content matches narration
- Check if mathematical operations align with voice explanation

### Method 3: Frame-by-Frame Analysis

For precise timing verification:

```bash
# Extract frames at specific times
ffmpeg -i linear_equation_elevenlabs_narrated.mp4 -ss 00:00:03 -frames:v 1 frame_3s.png
ffmpeg -i linear_equation_elevenlabs_narrated.mp4 -ss 00:00:06 -frames:v 1 frame_6s.png
ffmpeg -i linear_equation_elevenlabs_narrated.mp4 -ss 00:00:09 -frames:v 1 frame_9s.png

# View frames
# macOS: open frame_*.png
# Linux: eog frame_*.png
```

**What to check:**
- Does the visual at 3s match "isolate the variable x"?
- Does the visual at 6s show "subtract 3 from both sides"?
- Does the visual at 9s show "2x = 4"?

### Method 4: Audio Waveform Analysis

Visualize where audio occurs:

```bash
# Generate waveform image
ffmpeg -i linear_equation_elevenlabs_narrated.mp4 -filter_complex \
  "showwavespic=s=1920x1080" -frames:v 1 waveform.png

# View waveform
open waveform.png  # macOS
eog waveform.png   # Linux
```

**What to check:**
- Are there silent gaps where expected?
- Does audio spread evenly across video duration?
- Any unexpected clipping or cutoffs?

---

## Tools and Utilities

### VideoAudioSyncValidator

Main validation class with these methods:

| Method | Purpose | Returns |
|--------|---------|---------|
| `check_audio_presence()` | Verify audio track exists | bool |
| `get_video_duration()` | Get video length in seconds | float |
| `get_audio_duration()` | Get audio length in seconds | float |
| `check_sync_alignment()` | Compare audio/video durations | (bool, str) |
| `validate_narration_timing()` | Check cues within duration | List[str] |
| `generate_subtitle_file()` | Create SRT subtitle file | Path |
| `extract_audio_track()` | Extract audio for analysis | Path |

### Helper Functions

```python
from test_voice_video_sync import (
    check_narration_pacing,
    validate_narration_content_consistency
)

# Check pacing (gaps between cues)
pacing_issues = check_narration_pacing(
    narration_cues,
    min_gap=2.0,  # Minimum 2s between cues
    max_gap=10.0  # Maximum 10s between cues
)

# Check content coverage
expected_topics = ["equation", "subtract", "divide", "solution"]
content_ok, issues = validate_narration_content_consistency(
    narration_cues,
    expected_topics
)
```

### FFmpeg Commands

**Get video info:**
```bash
ffprobe -v error -show_format -show_streams video.mp4
```

**Extract audio only:**
```bash
ffmpeg -i video.mp4 -vn -acodec mp3 audio.mp3
```

**Check A/V sync:**
```bash
ffmpeg -i video.mp4 -f null - 2>&1 | grep "A-V"
```

---

## Common Issues and Fixes

### Issue 1: Audio Longer Than Video

**Symptom:**
```
❌ Sync issue: video=15.0s, audio=17.5s, diff=2.5s > 1.0s
```

**Causes:**
- Narration cues too close to end
- Long conclusion that extends past video
- FFmpeg padding added during combination

**Fix:**
```python
# Adjust last narration cue timing
script = AnimationScript("Topic")
script.add_intro("Intro text")
script.add_step("Step 1", time=3.0)
script.add_conclusion("Conclusion", time=12.0)  # Move earlier, not 15.0
```

### Issue 2: Narration Too Fast

**Symptom:**
```
⚠️ Too fast: 1.5s gap between cues at 3.0s and 4.5s
```

**Causes:**
- Cues scheduled too close together
- Not enough time for viewers to absorb information

**Fix:**
```python
# Increase gaps between cues (minimum 2-3 seconds)
script.add_step("Step 1", time=3.0)
script.add_step("Step 2", time=6.0)  # 3s gap, not 4.5s
script.add_step("Step 3", time=9.0)  # 3s gap
```

### Issue 3: Narration Past Video End

**Symptom:**
```
⚠️ Cue at 17.0s is near/past end (16.0s): 'Therefore, x equals 2...'
```

**Causes:**
- Last cue scheduled after video ends
- Video rendering took less time than expected

**Fix:**
```python
# Buffer time before end
video_duration = 16.0
buffer = 1.0
last_cue_time = video_duration - buffer - 3.0  # Account for speech duration

script.add_conclusion("Final words", time=last_cue_time)
```

### Issue 4: Missing Expected Topics

**Symptom:**
```
❌ Missing topic in narration: 'x = 2'
```

**Causes:**
- Narration script doesn't mention key concept
- Topic phrased differently than expected

**Fix:**
```python
# Ensure critical topics are mentioned
script.add_conclusion("Therefore, x equals 2. That's our solution!")
#                                    ^^^^^^^^ Explicitly state solution
```

### Issue 5: Visual-Voice Mismatch

**Symptom:**
- Video shows step at time X, but voice describes it at time Y
- Manual review reveals timing drift

**Causes:**
- Manim animation timing doesn't match expected durations
- Narration script written before seeing actual video

**Fix:**
```python
# Option 1: Adjust narration to match video
# After generating video, check actual visual timing and update script

# Option 2: Add timing requirements to video generation
result = engine.generate(
    topic="...",
    requirements="""
    Keep each step visible for EXACTLY 3 seconds:
    - 0-3s: Show equation
    - 3-6s: Show subtract step
    - 6-9s: Show divide step
    ...
    """
)
```

---

## Best Practices

### 1. Design Narration with Video Timing

**Good:**
```python
# Narration timed to match video structure
script = AnimationScript("Linear Equation")
script.add_intro("Let's solve this equation", time=0.0)
script.add_step("Subtract 3 from both sides", time=5.0)  # After equation appears
script.add_step("This gives us 2x = 4", time=8.0)       # After subtraction shown
script.add_conclusion("x equals 2", time=12.0)          # After solution shown
```

**Bad:**
```python
# Narration scheduled without considering visuals
script.add_step("Subtract 3", time=2.0)  # Too early, equation not visible yet
script.add_step("x equals 2", time=20.0) # Too late, past video end
```

### 2. Provide Visual Timing Requirements

```python
requirements = """
Clear timing structure:
- 0-3s: Title and equation display
- 3-6s: Subtract operation (visual shown)
- 6-9s: Result 2x = 4 (visual shown)
- 9-12s: Divide operation (visual shown)
- 12-15s: Final solution x = 2 (highlighted)

Each step should be visible for FULL 3 seconds before transitioning.
"""
```

### 3. Always Generate Subtitles

Subtitles are the easiest way to verify sync:

```python
# Include in all tests
srt_path = validator.generate_subtitle_file(narration_cues)
print(f"Review subtitles: {srt_path}")
```

### 4. Test with Multiple Gap Tolerances

```python
# Check different pacing requirements
strict_pacing = check_narration_pacing(cues, min_gap=3.0, max_gap=6.0)
relaxed_pacing = check_narration_pacing(cues, min_gap=2.0, max_gap=10.0)
```

### 5. Validate Before and After Rendering

**Before rendering:**
```python
# Validate narration script makes sense
assert len(script.cues) >= 3, "Need at least intro, body, conclusion"
assert script.cues[0].time == 0.0, "Start at beginning"
assert all(c1.time < c2.time for c1, c2 in zip(cues[:-1], cues[1:])), "Ascending order"
```

**After rendering:**
```python
# Validate actual output
validator = VideoAudioSyncValidator(video_path)
assert validator.check_audio_presence(), "Must have audio"
is_aligned, msg = validator.check_sync_alignment()
assert is_aligned, f"Sync issue: {msg}"
```

### 6. Document Expected Timing

Include timing expectations in test metadata:

```python
meta_content = f"""
Expected Timing:
  Video Duration: ~16s
  Narration Cues: 6
  Average Gap: 3s
  Topics Covered: equation, subtract, divide, solution

Actual Results:
  Video Duration: {actual_duration}s
  Audio Duration: {audio_duration}s
  Sync Drift: {drift}s
"""
```

### 7. Use Consistent Cue Duration

```python
# When generating subtitles, use realistic durations
srt_path = validator.generate_subtitle_file(
    narration_cues,
    cue_duration=3.0  # 3 seconds per subtitle (readable)
)
```

---

## Checklist for Voice-Video Consistency

Use this checklist when reviewing narrated videos:

### Automated Checks
- [ ] Audio track present (`check_audio_presence()`)
- [ ] Duration alignment within 1s (`check_sync_alignment()`)
- [ ] All cues within video duration (`validate_narration_timing()`)
- [ ] Pacing reasonable 2-10s gaps (`check_narration_pacing()`)
- [ ] Expected topics covered (`validate_narration_content_consistency()`)
- [ ] Subtitle file generated

### Manual Checks
- [ ] Play video start-to-finish with subtitles
- [ ] Voice matches visual at each key timestamp
- [ ] No awkward pauses or rushed segments
- [ ] Mathematical terminology pronounced correctly
- [ ] Final solution clearly stated and shown
- [ ] Background music (if any) doesn't overpower voice
- [ ] Audio quality is clear and consistent

### Educational Quality
- [ ] Narration explains WHY, not just WHAT
- [ ] Steps are in logical order
- [ ] Visual reinforces what voice describes
- [ ] Appropriate pace for target audience
- [ ] Key concepts emphasized both visually and verbally

---

## Example: Complete Validation Workflow

```python
def validate_educational_video(video_path, script):
    """Complete validation workflow for educational videos."""

    validator = VideoAudioSyncValidator(video_path)

    # 1. Basic checks
    assert validator.check_audio_presence(), "No audio track"

    # 2. Duration alignment
    is_aligned, msg = validator.check_sync_alignment(tolerance_seconds=1.0)
    print(f"Duration: {msg}")

    # 3. Timing validation
    cues = [(c.time, c.text) for c in script.cues]
    timing_issues = validator.validate_narration_timing(cues)
    print(f"Timing: {timing_issues}")

    # 4. Pacing check
    pacing_issues = check_narration_pacing(cues, min_gap=2.0, max_gap=8.0)
    print(f"Pacing: {pacing_issues}")

    # 5. Content check
    expected = ["equation", "subtract", "divide", "solution"]
    content_ok, issues = validate_narration_content_consistency(cues, expected)
    print(f"Content: {issues}")

    # 6. Generate review materials
    srt_path = validator.generate_subtitle_file(cues)
    print(f"\n✅ Validation complete!")
    print(f"   Review video with subtitles: {srt_path}")

    return {
        'has_audio': True,
        'aligned': is_aligned,
        'timing_ok': len([i for i in timing_issues if '❌' in i]) == 0,
        'pacing_ok': len([i for i in pacing_issues if '❌' in i]) == 0,
        'content_ok': content_ok,
        'subtitle_file': srt_path
    }
```

---

## Additional Resources

- **FFmpeg Documentation**: https://ffmpeg.org/documentation.html
- **SRT Subtitle Format**: https://en.wikipedia.org/wiki/SubRip
- **Video Accessibility**: https://www.w3.org/WAI/media/av/
- **Educational Video Best Practices**: See project's `curriculum/` directory

---

**Questions or Issues?**

Open an issue on GitHub or check `tests/README_ELEVENLABS_TESTS.md` for more information.
