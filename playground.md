# Playground — Prompt Tuning UI

A web-based developer tool for iterating on LLM prompts across the full content pipeline. Edit prompts, execute pipeline stages, tune LLM parameters, and compare outputs — all from the browser.

## Prerequisites

1. **Python 3.10–3.12** (not 3.13+)

2. **Install with API dependencies:**
   ```bash
   pip install -e ".[api]"
   ```

3. **Create a `.env` file** in the project root with your API key:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```
   Or, if using OpenAI:
   ```
   OPENAI_API_KEY=sk-proj-...
   MATH_ENGINE_LLM_PROVIDER=openai
   ```

## Starting the Backend

```bash
source .env && python -m math_content_engine.api.server
```

The FastAPI server starts on port 8000. You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verify it's running:**

```bash
curl http://localhost:8000/health
# → {"status": "healthy", ...}
```

**Other useful URLs:**
- Swagger API docs: http://localhost:8000/docs
- Root info endpoint: http://localhost:8000/

## Opening the Frontend

Open **http://localhost:8000/playground/** in your browser.

The frontend is served as static files by the same FastAPI server. There is no separate frontend process, no npm, no webpack, no build step. It is vanilla HTML, JavaScript, and CSS served directly by FastAPI's `StaticFiles`.

## Using the Playground

### 1. Upload Content

- Paste or type textbook markdown into the main textarea
- Select a student interest from the dropdown (e.g. Basketball, Music, Gaming, Cooking)
- The interest determines the personalization theme applied to the content

### 2. Navigate to a Pipeline Stage

Click a stage in the left sidebar:

| Stage | What it does |
|-------|-------------|
| **Upload Content** | Paste textbook markdown, pick interest |
| **Extract Concepts** | Identify math concepts in the content (returns JSON) |
| **Personalize** | Transform textbook into an interest-themed version |
| **Gen. Animation** | Generate Manim Python code for a math topic |
| **Render Video** | Compile Manim code into an MP4 video |

### 3. Preview Prompts

Click **"Preview Prompts"** to load the system and user prompts that would be sent to the LLM. This calls the backend's prompt builder without making any LLM calls — it just shows you what the prompts look like.

### 4. Edit Prompts

Both the **System Prompt** and **User Prompt** are displayed in editable textareas. Modify them directly:

- Change the tone or style instructions in the system prompt
- Adjust the task description in the user prompt
- Add or remove constraints, examples, or formatting rules

Click **"Reset"** next to either prompt to restore the original default.

### 5. Execute

Click **"Execute ▶"** to run the stage. The request is sent to the backend, which:

1. Creates a background task
2. Streams progress via Server-Sent Events (SSE)
3. Returns the result when complete

A progress bar shows "Running..." during execution. The output appears below the prompts when done, along with metadata (duration, token count, model used).

### 6. Compare Runs

The **Run History** panel in the left sidebar tracks every execution with:
- Stage name
- Timestamp
- Green dot (success) or red dot (failure)

Click a history entry to view that run's output.

## LLM Settings

The collapsible **LLM Settings** bar at the top of the main panel controls:

| Setting | Control | Notes |
|---------|---------|-------|
| **Temperature** | Slider (0.00–1.00) | 0 = deterministic, 1 = creative. Default: 0.70 |
| **Max Tokens** | Dropdown (2K / 4K / 8K / 16K) | Caps response length. Default: 4,096 |
| **Model** | Read-only badge | Set via env var or config |
| **Provider** | Read-only badge | `claude` or `openai`, set via `MATH_ENGINE_LLM_PROVIDER` |

Temperature and max tokens are sent with every execute request. To change the model or provider, update your `.env` file and restart the server.

## API Endpoints

All playground endpoints are prefixed with `/api/v1/playground/`.

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/config` | Server config: LLM provider, model, available interests, temperature, max_tokens |
| `GET` | `/interests` | List all available interest profiles with details |
| `GET` | `/interests/{name}` | Get a single interest profile |
| `POST` | `/prompts/preview` | Preview prompts for a stage without calling the LLM |
| `POST` | `/execute` | Start a pipeline stage in the background (returns `task_id`) |
| `GET` | `/tasks/{id}` | Poll task status and result |
| `GET` | `/tasks/{id}/stream` | SSE event stream for real-time progress |
| `POST` | `/upload/textbook` | Upload textbook content (multipart or JSON) |
| `GET` | `/files/video/{name}` | Serve a rendered MP4 video |
| `GET` | `/files/code/{name}` | Serve a generated Python file |

### Example: Preview prompts via curl

```bash
curl -X POST http://localhost:8000/api/v1/playground/prompts/preview \
  -H "Content-Type: application/json" \
  -d '{"stage": "personalize", "textbook_content": "# Linear Equations\n...", "interest": "basketball"}'
```

### Example: Execute a stage via curl

```bash
# Start execution (returns task_id)
curl -X POST http://localhost:8000/api/v1/playground/execute \
  -H "Content-Type: application/json" \
  -d '{
    "stage": "personalize",
    "textbook_content": "# Linear Equations\n...",
    "interest": "basketball",
    "temperature": 0.7,
    "max_tokens": 4096
  }'

# Stream progress
curl -N http://localhost:8000/api/v1/playground/tasks/{task_id}/stream
```

## Architecture

```
Browser (vanilla HTML/JS/CSS, no build step)
    ↓  fetch() / EventSource (SSE)
FastAPI Server (single process)
    ├── /playground/             → StaticFiles serves index.html, app.js, styles.css
    ├── /api/v1/playground/*     → Playground backend (prompt preview, execute, tasks)
    └── /api/v1/videos/*         → Existing video API (unchanged)
```

### Backend files

```
src/math_content_engine/api/playground/
├── __init__.py          # Exports playground_router
├── models.py            # Pydantic models (PromptPreview, StageExecuteRequest, etc.)
├── prompt_builder.py    # Builds prompts for preview without LLM calls
├── pipeline_runner.py   # Wraps pipeline steps with prompt override support
├── routes.py            # All /api/v1/playground/* FastAPI endpoints
└── tasks.py             # Async TaskManager with SSE streaming via asyncio.to_thread
```

### Frontend files

```
src/math_content_engine/static/playground/
├── index.html    # Page layout, stage panels, forms
├── app.js        # State management, API calls, SSE handling, UI logic
└── styles.css    # Dark theme, responsive layout
```

## Troubleshooting

**Server won't start — `ANTHROPIC_API_KEY environment variable is required`**
- Make sure `.env` exists in the project root and contains your key
- Run `source .env` before starting the server, or use: `source .env && python -m math_content_engine.api.server`

**Playground page is blank / 404**
- Ensure you installed with `pip install -e ".[api]"` (not just `pip install -e .`)
- Check that `src/math_content_engine/static/playground/index.html` exists
- Visit http://localhost:8000/docs to confirm the server is running

**"Preview Prompts" returns empty textareas**
- Make sure you've entered textbook content and selected an interest first (for Personalize stage)
- For Generate Animation, fill in the Topic field before previewing

**Execute hangs or never completes**
- Check the terminal running the server for error tracebacks
- The LLM call typically takes 8–20 seconds depending on content length
- If the progress bar stays on "Running..." after 60+ seconds, the LLM call may have failed — check server logs
