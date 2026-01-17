# Animation Prompt Engineering Lab

## Overview

A tool for **prompt engineering** math animations. Helps users:

1. **Edit prompts easily** - Modify topic, requirements, style instructions
2. **See what you get** - View generated code and rendered video together
3. **Get suggestions** - AI-powered hints on how to change prompts to achieve desired video changes

## Installation

```bash
# Install with lab dependencies
pip install -e ".[lab]"
```

## Quick Start

```bash
# Start a new interactive session
math-lab new "Pythagorean theorem" -i

# Or with initial requirements
math-lab new "Quadratic formula" -r "Show graphical solution" -i

# List existing sessions
math-lab list

# Resume a session
math-lab resume ses_abc123
```

## Interactive Commands

Once in interactive mode (`prompt>`), you have these commands:

### Prompt Editing
```
prompt              Show current prompt
add <text>          Add a requirement
remove <n>          Remove requirement #n
topic <text>        Change the topic
style <dark|light>  Change animation style
pacing <slow|medium|fast>  Set animation pacing
```

### Generation & Preview
```
generate            Generate code and render video
generate --no-render  Generate code only (skip rendering)
show [version]      Show generated code
play [version]      Open video in player
render [version]    Render a version that wasn't rendered
```

### Suggestions (Key Feature!)
```
ask <question>      Get suggestions for prompt changes
                    Examples:
                    - ask how do I make it slower?
                    - ask how to show one element at a time?
                    - ask how to add more colors?

suggest             Get general improvement suggestions
```

### Comparison
```
versions            List all versions
compare <n> <m>     Compare two versions (prompt + code diff)
diff <n> <m>        Show code diff between versions
```

### Export
```
export [file]       Export current code to file
```

## Example Session

```
$ math-lab new "Pythagorean theorem" -i

============================================================
         Animation Prompt Engineering Lab
============================================================
  Session: ses_abc123
  Topic:   Pythagorean theorem
============================================================

--- PROMPT ----------------------------------------------------
Topic: Pythagorean theorem
Requirements: (none)
Style: dark | Audience: high school
--------------------------------------------------------------

prompt> add Show visual proof with squares on each side
✓ Added: "Show visual proof with squares on each side"

prompt> generate

Generating v1...
✓ Code generated: PythagoreanScene (45 lines)
✓ Rendered in 8.2s → .lab/output/ses_abc123/v1.mp4

prompt> play
Opening: .lab/output/ses_abc123/v1.mp4

prompt> ask how do I make the squares appear one at a time?

--- SUGGESTIONS ---

1. Show elements one at a time
   + "Animate elements one at a time, not simultaneously"
   + "Show each element separately with a pause between"

Apply suggestion? [1/none]: 1
✓ Suggestion applied!

prompt> generate

Generating v2...
✓ Code generated: PythagoreanScene (52 lines)
✓ Rendered in 10.1s → .lab/output/ses_abc123/v2.mp4

prompt> compare 1 2

--- COMPARISON: v1 → v2 ---

Prompt changes:
  + Animate elements one at a time, not simultaneously
  + Show each element separately with a pause between

Code: 45 → 52 lines (+7)

prompt> export pythagorean.py
✓ Exported → pythagorean.py

prompt> quit
Session saved. Resume with: math-lab resume ses_abc123
```

## Suggestion Patterns

The `ask` command recognizes these common requests:

| What you want | What to ask |
|--------------|-------------|
| Slower animation | "slower", "more time", "longer pauses" |
| Faster animation | "faster", "quicker", "speed up" |
| Sequential elements | "one at a time", "step by step", "sequential" |
| More colors | "more colors", "colorful", "vibrant" |
| Simpler | "simpler", "basic", "minimal" |
| More detail | "more detail", "elaborate", "thorough" |
| Add labels | "labels", "text", "annotate" |
| Bigger text | "bigger text", "larger font" |
| Show formula | "formula", "equation", "show the math" |
| Draw gradually | "draw", "trace", "gradually" |
| Zoom effects | "zoom", "focus", "close up" |

## File Structure

```
src/math_content_engine/lab/
├── __init__.py
├── cli.py                      # CLI entry point (math-lab)
├── prompt/
│   ├── models.py               # AnimationPrompt, GenerationResult, PromptSession
├── session/
│   ├── storage.py              # SQLite persistence
│   ├── manager.py              # Session lifecycle + generation
├── suggest/
│   ├── patterns.py             # Keyword → suggestion mapping
│   ├── engine.py               # SuggestionEngine
├── compare/
│   ├── diff.py                 # Prompt and code diffing
└── interactive/
    └── repl.py                 # Interactive REPL
```

## Data Storage

Sessions are stored in `.lab/sessions.db` (SQLite) in your project directory.
Generated videos and code are stored in `.lab/output/<session_id>/`.

## CLI Commands (Non-interactive)

```bash
# Create session
math-lab new "Topic" [-r requirement] [-i] [--style dark|light]

# Session management
math-lab list [-n limit]
math-lab show <session-id>
math-lab resume <session-id>
math-lab delete <session-id> [--force]

# Generation
math-lab generate <session-id> [-q l|m|h] [--no-render]

# Export
math-lab export <session-id> [-v version] [-o output.py]
```
