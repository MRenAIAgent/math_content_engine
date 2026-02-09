/* ================================================================
   Math Content Playground — Frontend Application
   Single-page collapsible pipeline with batch animation generation
   ================================================================ */

const API = "/api/v1/playground";

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

const state = {
    textbookContent: "",
    config: {},
    // LLM settings (user-tunable)
    llmSettings: {
        temperature: 0.7,
        maxTokens: 4096,
    },
    // Global student & engagement settings
    studentSettings: {
        interest: "",
        studentName: "",
        preferredAddress: "",
        gradeLevel: "",
        city: "",
        state: "",
        favoriteFigure: "",
        favoriteTeam: "",
    },
    // Default prompts (from preview endpoint)
    defaultPrompts: {
        personalize: { system: "", user: "" },
        extract_concepts: { system: "", user: "" },
        generate_animation: { system: "", user: "" },
    },
    // Current outputs
    outputs: {
        concepts: null,
        personalized: null,
        animation_code: null,
        scene_name: null,
        video_path: null,
    },
    // Extracted concepts for batch generation
    extractedConcepts: [],
    // Batch generation results: { conceptName: { code, scene_name, video_filename, status } }
    batchResults: {},
    // Pipeline status tracking
    pipelineStatus: {
        upload: "empty",
        extract_concepts: "empty",
        personalize: "empty",
        generate_animation: "empty",
        render: "empty",
    },
    // Run history
    history: [],
};

// ---------------------------------------------------------------------------
// Initialization
// ---------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", async () => {
    await loadConfig();
    if (typeof marked !== "undefined") {
        marked.setOptions({
            highlight: (code, lang) => {
                if (typeof hljs !== "undefined" && lang && hljs.getLanguage(lang)) {
                    return hljs.highlight(code, { language: lang }).value;
                }
                return code;
            },
        });
    }
});

async function loadConfig() {
    try {
        const resp = await fetch(`${API}/config`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        state.config = await resp.json();

        document.getElementById("config-provider").textContent =
            state.config.llm_provider || "?";
        document.getElementById("config-model").textContent =
            state.config.model || "";

        state.llmSettings.temperature = state.config.temperature || 0.7;
        state.llmSettings.maxTokens = state.config.max_tokens || 4096;
        initLLMSettingsUI();

        state.availableInterests = state.config.available_interests || [];
    } catch (err) {
        showToast(`Failed to load config: ${err.message}`, "error");
    }
}

// ---------------------------------------------------------------------------
// Section Toggle (replaces switchStage)
// ---------------------------------------------------------------------------

function toggleSection(stage) {
    const body = document.getElementById(`body-${stage}`);
    const chevron = document.getElementById(`chevron-${stage}`);
    if (!body) return;

    const isVisible = body.classList.contains("visible");
    body.classList.toggle("visible", !isVisible);
    if (chevron) {
        chevron.classList.toggle("expanded", !isVisible);
    }

    // Auto-load prompts when opening a section with prompt editors
    if (!isVisible && ["personalize", "extract_concepts", "generate_animation"].includes(stage)) {
        const sysEl = document.getElementById(`prompt-${stage}-system`);
        if (sysEl && !sysEl.value) {
            previewPrompts(stage);
        }
    }
}

// ---------------------------------------------------------------------------
// Pipeline Status Management
// ---------------------------------------------------------------------------

function updatePipelineStatus(stage, status) {
    state.pipelineStatus[stage] = status;
    const el = document.getElementById(`status-${stage}`);
    if (!el) return;

    el.className = `section-status ${status}`;
    const labels = {
        empty: "",
        completed: "Done",
        stale: "Stale",
        running: "Running...",
    };
    el.textContent = labels[status] || "";
}

function markDownstreamStale(fromStage) {
    const pipeline = ["upload", "extract_concepts", "personalize", "generate_animation", "render"];
    const idx = pipeline.indexOf(fromStage);
    if (idx < 0) return;

    for (let i = idx + 1; i < pipeline.length; i++) {
        const s = pipeline[i];
        if (state.pipelineStatus[s] === "completed") {
            updatePipelineStatus(s, "stale");
        }
    }
}

// ---------------------------------------------------------------------------
// Textbook input
// ---------------------------------------------------------------------------

function onTextbookInput() {
    const textarea = document.getElementById("textbook-input");
    state.textbookContent = textarea.value;
    const stats = document.getElementById("upload-stats");
    if (state.textbookContent) {
        const len = state.textbookContent.length;
        stats.textContent = `${len.toLocaleString()} chars`;
        updatePipelineStatus("upload", "completed");
        markDownstreamStale("upload");
    } else {
        stats.textContent = "";
        updatePipelineStatus("upload", "empty");
    }
}

function onContentChanged() {
    updatePipelineStatus("upload", "completed");
    markDownstreamStale("upload");

    // Auto-trigger concept extraction if content is long enough
    if (state.textbookContent && state.textbookContent.length > 50) {
        autoExtractConcepts();
    }
}

// ---------------------------------------------------------------------------
// Auto concept extraction
// ---------------------------------------------------------------------------

async function autoExtractConcepts() {
    if (!state.textbookContent) return;

    updatePipelineStatus("extract_concepts", "running");
    setStageLoading("extract_concepts", true);

    const body = {
        stage: "extract_concepts",
        textbook_content: state.textbookContent,
        temperature: state.llmSettings.temperature,
        max_tokens: state.llmSettings.maxTokens,
    };

    try {
        const resp = await fetch(`${API}/execute`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
        if (!resp.ok) {
            updatePipelineStatus("extract_concepts", "stale");
            setStageLoading("extract_concepts", false);
            return;
        }
        const { task_id } = await resp.json();
        connectSSE(task_id, "extract_concepts");
    } catch (err) {
        updatePipelineStatus("extract_concepts", "stale");
        setStageLoading("extract_concepts", false);
    }
}

// ---------------------------------------------------------------------------
// Global Student & Engagement Settings
// ---------------------------------------------------------------------------

function toggleStudentSettings() {
    const panel = document.getElementById("student-settings-panel");
    const chevron = document.getElementById("student-settings-chevron");
    const isVisible = panel.classList.contains("visible");
    panel.classList.toggle("visible", !isVisible);
    chevron.classList.toggle("expanded", !isVisible);
}

function onGlobalInterestChange() {
    const input = document.getElementById("global-interest");
    state.studentSettings.interest = (input.value || "").trim();
    updateStudentSettingsSummary();
}

function onGlobalSettingChange() {
    state.studentSettings.studentName = (document.getElementById("global-student-name").value || "").trim();
    state.studentSettings.preferredAddress = (document.getElementById("global-preferred-address").value || "").trim();
    state.studentSettings.gradeLevel = (document.getElementById("global-grade-level").value || "").trim();
    state.studentSettings.city = (document.getElementById("global-city").value || "").trim();
    state.studentSettings.state = (document.getElementById("global-state").value || "").trim();
    state.studentSettings.favoriteFigure = (document.getElementById("global-favorite-figure").value || "").trim();
    state.studentSettings.favoriteTeam = (document.getElementById("global-favorite-team").value || "").trim();
    updateStudentSettingsSummary();
}

function updateStudentSettingsSummary() {
    const el = document.getElementById("student-settings-summary");
    if (!el) return;

    const parts = [];
    const s = state.studentSettings;
    if (s.interest) parts.push(s.interest);
    if (s.studentName) parts.push(s.studentName);
    if (s.city || s.state) parts.push([s.city, s.state].filter(Boolean).join(", "));
    if (s.favoriteFigure) parts.push(s.favoriteFigure);
    if (s.favoriteTeam) parts.push(s.favoriteTeam);

    el.textContent = parts.length > 0 ? parts.join(", ") : "";
}

function getGlobalStudentFields() {
    const s = state.studentSettings;
    const fields = {};
    if (s.interest) fields.interest = s.interest;
    if (s.studentName) fields.student_name = s.studentName;
    if (s.preferredAddress) fields.preferred_address = s.preferredAddress;
    if (s.gradeLevel) fields.grade_level = s.gradeLevel;
    if (s.city) fields.city = s.city;
    if (s.state) fields.state = s.state;
    if (s.favoriteFigure) fields.favorite_figure = s.favoriteFigure;
    if (s.favoriteTeam) fields.favorite_team = s.favoriteTeam;
    return fields;
}

function loadSampleContent() {
    const sample = `# Chapter 2: Solving Linear Equations

## 2.1 One-Step Equations

A **linear equation** is an equation that can be written in the form ax + b = c.

### Example 1: Solving x + 5 = 12

**Problem:** Solve for x in the equation x + 5 = 12.

**Solution:**
1. Subtract 5 from both sides: x + 5 - 5 = 12 - 5
2. Simplify: x = 7

**Verification:** 7 + 5 = 12 \u2713

### Example 2: Solving 3x = 21

**Problem:** Solve for x in the equation 3x = 21.

**Solution:**
1. Divide both sides by 3: 3x / 3 = 21 / 3
2. Simplify: x = 7

## 2.2 Two-Step Equations

### Example 3: Solving 2x + 3 = 11

**Problem:** Solve for x in the equation 2x + 3 = 11.

**Solution:**
1. Subtract 3 from both sides: 2x + 3 - 3 = 11 - 3
2. Simplify: 2x = 8
3. Divide both sides by 2: x = 4

**Verification:** 2(4) + 3 = 8 + 3 = 11 \u2713

## Practice Problems

1. Solve: x - 8 = 15
2. Solve: 5x = 45
3. Solve: 4x + 7 = 31
4. Solve: 2x - 9 = 13
`;
    document.getElementById("textbook-input").value = sample;
    state.textbookContent = sample;
    onTextbookInput();
    onContentChanged();
    showToast("Sample textbook loaded", "info");
}

// ---------------------------------------------------------------------------
// File upload
// ---------------------------------------------------------------------------

async function onFileUpload() {
    const fileInput = document.getElementById("textbook-file-input");
    const file = fileInput.files[0];
    if (!file) return;

    const progress = document.getElementById("progress-upload");
    progress.style.display = "flex";
    document.getElementById("progress-text-upload").textContent = `Uploading ${file.name}...`;

    try {
        const formData = new FormData();
        formData.append("file", file);

        const resp = await fetch(`${API}/upload/textbook`, {
            method: "POST",
            body: formData,
        });

        if (!resp.ok) {
            const err = await resp.json();
            showToast(err.detail || "Upload failed", "error");
            return;
        }

        const data = await resp.json();
        document.getElementById("textbook-input").value = data.content;
        state.textbookContent = data.content;
        onTextbookInput();
        onContentChanged();

        const sourceLabels = {
            mathpix_cached: "Loaded from cached Mathpix markdown",
            mathpix: "Parsed via Mathpix (math-aware OCR)",
            pymupdf: "Parsed via PyMuPDF (basic text extraction)",
            pdfplumber: "Parsed via pdfplumber (basic text extraction)",
            raw: "Loaded",
        };
        const label = sourceLabels[data.source] || "Loaded";
        showToast(`${label}: ${file.name} (${data.length.toLocaleString()} chars)`, "success");
    } catch (err) {
        showToast(`Upload error: ${err.message}`, "error");
    } finally {
        progress.style.display = "none";
    }
}

// ---------------------------------------------------------------------------
// Concept Checklist (for batch animation generation)
// ---------------------------------------------------------------------------

function renderConceptChecklist(concepts) {
    state.extractedConcepts = concepts;
    const area = document.getElementById("concept-selector-area");
    const checklist = document.getElementById("concept-checklist");
    const batchBtn = document.getElementById("btn-batch-generate");

    if (!concepts || concepts.length === 0) {
        area.style.display = "none";
        batchBtn.style.display = "none";
        return;
    }

    area.style.display = "block";
    batchBtn.style.display = "inline-flex";

    let html = "";
    for (const c of concepts) {
        const id = c.concept_id || c.suggested_id || c.name;
        const name = c.name || id;
        const confidence = c.confidence ? Math.round(c.confidence * 100) : null;
        html += `<div class="concept-check-item">
            <input type="checkbox" id="concept-chk-${esc(id)}" value="${esc(name)}" checked />
            <span class="concept-name">${esc(name)}</span>
            ${confidence !== null ? `<span class="concept-confidence">${confidence}%</span>` : ""}
        </div>`;
    }
    checklist.innerHTML = html;
}

function selectAllConcepts(checked) {
    const checklist = document.getElementById("concept-checklist");
    const boxes = checklist.querySelectorAll('input[type="checkbox"]');
    boxes.forEach((box) => { box.checked = checked; });
}

function getSelectedConcepts() {
    const checklist = document.getElementById("concept-checklist");
    const boxes = checklist.querySelectorAll('input[type="checkbox"]:checked');
    return Array.from(boxes).map((box) => box.value);
}

// ---------------------------------------------------------------------------
// Prompt preview
// ---------------------------------------------------------------------------

async function previewPrompts(stage) {
    const body = buildPreviewRequest(stage);
    if (!body) return;

    try {
        const resp = await fetch(`${API}/prompts/preview`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
        if (!resp.ok) {
            const err = await resp.json();
            showToast(err.detail || "Failed to preview prompts", "error");
            return;
        }
        const data = await resp.json();

        state.defaultPrompts[stage] = {
            system: data.system_prompt,
            user: data.user_prompt,
        };

        document.getElementById(`prompt-${stage}-system`).value = data.system_prompt;
        document.getElementById(`prompt-${stage}-user`).value = data.user_prompt;

        showToast("Prompts loaded", "success");
    } catch (err) {
        showToast(`Error: ${err.message}`, "error");
    }
}

function buildPreviewRequest(stage) {
    const req = { stage };
    const globals = getGlobalStudentFields();

    if (stage === "personalize") {
        if (!state.textbookContent) {
            showToast("Upload textbook content first", "error");
            return null;
        }
        if (!globals.interest) {
            showToast("Set an interest in Student & Engagement settings", "error");
            return null;
        }
        req.textbook_content = state.textbookContent;
        req.interest = globals.interest;
    } else if (stage === "extract_concepts") {
        if (!state.textbookContent) {
            showToast("Upload textbook content first", "error");
            return null;
        }
        req.textbook_content = state.textbookContent;
    } else if (stage === "generate_animation") {
        const topic = document.getElementById("anim-topic").value;
        if (!topic) {
            showToast("Enter a topic", "error");
            return null;
        }
        req.topic = topic;
        req.requirements = document.getElementById("anim-requirements").value || "";
        req.animation_style = document.getElementById("anim-style").value;
        req.audience_level = document.getElementById("anim-audience").value;
        if (state.textbookContent) {
            req.textbook_content = state.textbookContent;
        }
        Object.assign(req, globals);
    }
    return req;
}

function resetPrompt(stage, type) {
    const def = state.defaultPrompts[stage];
    if (def && def[type]) {
        document.getElementById(`prompt-${stage}-${type}`).value =
            type === "system" ? def.system : def.user;
        showToast("Prompt reset to default", "info");
    }
}

// ---------------------------------------------------------------------------
// Stage execution
// ---------------------------------------------------------------------------

async function executeStage(stage) {
    const body = buildExecuteRequest(stage);
    if (!body) return;

    setStageLoading(stage, true);
    updatePipelineStatus(stage, "running");

    try {
        const resp = await fetch(`${API}/execute`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
        if (!resp.ok) {
            const err = await resp.json();
            showToast(err.detail || "Execution failed", "error");
            setStageLoading(stage, false);
            updatePipelineStatus(stage, "stale");
            return;
        }
        const { task_id } = await resp.json();
        connectSSE(task_id, stage);
    } catch (err) {
        showToast(`Error: ${err.message}`, "error");
        setStageLoading(stage, false);
        updatePipelineStatus(stage, "stale");
    }
}

function buildExecuteRequest(stage) {
    const req = { stage };

    req.temperature = state.llmSettings.temperature;
    req.max_tokens = state.llmSettings.maxTokens;

    const sysEl = document.getElementById(`prompt-${stage}-system`);
    const usrEl = document.getElementById(`prompt-${stage}-user`);
    if (sysEl && usrEl) {
        const sysVal = sysEl.value;
        const usrVal = usrEl.value;
        const def = state.defaultPrompts[stage];
        if (
            (sysVal && sysVal !== def.system) ||
            (usrVal && usrVal !== def.user)
        ) {
            req.prompt_override = {};
            if (sysVal && sysVal !== def.system) req.prompt_override.system_prompt = sysVal;
            if (usrVal && usrVal !== def.user) req.prompt_override.user_prompt = usrVal;
        }
    }

    const globals = getGlobalStudentFields();

    if (stage === "personalize") {
        if (!state.textbookContent) {
            showToast("Upload textbook content first", "error");
            return null;
        }
        if (!globals.interest) {
            showToast("Set an interest in Student & Engagement settings", "error");
            return null;
        }
        req.textbook_content = state.textbookContent;
        req.interest = globals.interest;
    } else if (stage === "extract_concepts") {
        if (!state.textbookContent) {
            showToast("Upload textbook content first", "error");
            return null;
        }
        req.textbook_content = state.textbookContent;
    } else if (stage === "generate_animation") {
        const topic = document.getElementById("anim-topic").value;
        if (!topic) {
            showToast("Enter a topic", "error");
            return null;
        }
        req.topic = topic;
        req.requirements = document.getElementById("anim-requirements").value || "";
        req.animation_style = document.getElementById("anim-style").value;
        req.audience_level = document.getElementById("anim-audience").value;
        if (state.textbookContent) {
            req.textbook_content = state.textbookContent;
        }
        Object.assign(req, globals);
    }
    return req;
}

/** Execute a single animation (manual topic entry). */
function executeSingleAnimation() {
    executeStage("generate_animation");
}

async function executeRender() {
    const code = document.getElementById("render-code").value;
    if (!code) {
        showToast("No code to render. Generate animation first (step 4)", "error");
        return;
    }

    const match = code.match(/class\s+(\w+)\s*\(\s*Scene\s*\)/);
    const sceneName = match ? match[1] : "GeneratedScene";

    const body = {
        stage: "render",
        code: code,
        scene_name: sceneName,
        video_quality: document.getElementById("render-quality").value,
    };

    setStageLoading("render", true);
    updatePipelineStatus("render", "running");

    try {
        const resp = await fetch(`${API}/execute`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
        if (!resp.ok) {
            const err = await resp.json();
            showToast(err.detail || "Render failed", "error");
            setStageLoading("render", false);
            updatePipelineStatus("render", "stale");
            return;
        }
        const { task_id } = await resp.json();
        connectSSE(task_id, "render");
    } catch (err) {
        showToast(`Error: ${err.message}`, "error");
        setStageLoading("render", false);
        updatePipelineStatus("render", "stale");
    }
}

// ---------------------------------------------------------------------------
// Batch Animation Generation
// ---------------------------------------------------------------------------

async function executeBatchAnimations() {
    const selectedConcepts = getSelectedConcepts();
    if (selectedConcepts.length === 0) {
        showToast("Select at least one concept to animate", "error");
        return;
    }

    const batchBtn = document.getElementById("btn-batch-generate");
    batchBtn.disabled = true;
    updatePipelineStatus("generate_animation", "running");

    state.batchResults = {};
    const resultsContainer = document.getElementById("batch-results");
    resultsContainer.innerHTML = "";

    // Create cards for each concept
    for (const conceptName of selectedConcepts) {
        state.batchResults[conceptName] = { status: "pending", code: null, scene_name: null };
        resultsContainer.innerHTML += buildBatchCardHTML(conceptName, "pending");
    }

    // Generate animations sequentially
    for (const conceptName of selectedConcepts) {
        updateBatchCardStatus(conceptName, "generating");
        state.batchResults[conceptName].status = "generating";

        try {
            const result = await generateSingleConceptAnimation(conceptName);
            state.batchResults[conceptName] = {
                status: "done",
                code: result.code,
                scene_name: result.scene_name,
            };
            updateBatchCard(conceptName, result);
        } catch (err) {
            state.batchResults[conceptName].status = "error";
            updateBatchCardStatus(conceptName, "error", err.message);
        }
    }

    batchBtn.disabled = false;
    updatePipelineStatus("generate_animation", "completed");

    // Show batch render button
    const batchRenderBtn = document.getElementById("btn-batch-render");
    if (batchRenderBtn) {
        batchRenderBtn.style.display = "inline-flex";
    }

    showToast(`Generated ${selectedConcepts.length} animations`, "success");
}

async function generateSingleConceptAnimation(conceptName) {
    const globals = getGlobalStudentFields();
    const body = {
        stage: "generate_animation",
        topic: conceptName,
        requirements: document.getElementById("anim-requirements").value || "",
        animation_style: document.getElementById("anim-style").value,
        audience_level: document.getElementById("anim-audience").value,
        temperature: state.llmSettings.temperature,
        max_tokens: state.llmSettings.maxTokens,
        ...globals,
    };

    if (state.textbookContent) {
        body.textbook_content = state.textbookContent;
    }

    const resp = await fetch(`${API}/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });

    if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || "Generation failed");
    }

    const { task_id } = await resp.json();
    return await waitForTaskResult(task_id);
}

async function waitForTaskResult(taskId) {
    const maxPolls = 120;
    for (let i = 0; i < maxPolls; i++) {
        await sleep(2000);
        try {
            const resp = await fetch(`${API}/tasks/${taskId}`);
            if (!resp.ok) break;
            const data = await resp.json();

            if (data.status === "completed" && data.result) {
                return data.result.output;
            } else if (data.status === "failed") {
                throw new Error(data.result?.error || "Task failed");
            }
        } catch (err) {
            if (err.message !== "Task failed") continue;
            throw err;
        }
    }
    throw new Error("Task polling timed out");
}

function buildBatchCardHTML(conceptName, status) {
    const safeId = makeSafeId(conceptName);
    return `<div class="batch-result-card" id="batch-card-${safeId}">
        <div class="batch-result-header">
            <span class="concept-label">${esc(conceptName)}</span>
            <span class="batch-status ${status}" id="batch-status-${safeId}">${statusLabel(status)}</span>
        </div>
        <div class="batch-result-body" id="batch-body-${safeId}"></div>
    </div>`;
}

function updateBatchCardStatus(conceptName, status, errorMsg) {
    const safeId = makeSafeId(conceptName);
    const statusEl = document.getElementById(`batch-status-${safeId}`);
    if (statusEl) {
        statusEl.className = `batch-status ${status}`;
        statusEl.textContent = errorMsg ? `Error: ${errorMsg}` : statusLabel(status);
    }
}

function updateBatchCard(conceptName, result) {
    const safeId = makeSafeId(conceptName);
    const statusEl = document.getElementById(`batch-status-${safeId}`);
    const bodyEl = document.getElementById(`batch-body-${safeId}`);
    if (!statusEl || !bodyEl) return;

    statusEl.className = "batch-status done";
    statusEl.textContent = "Done";

    const code = result.code || "";
    let highlightedCode = esc(code);
    if (typeof hljs !== "undefined") {
        highlightedCode = hljs.highlight(code, { language: "python" }).value;
    }

    bodyEl.innerHTML = `
        <div class="batch-code-toggle" onclick="toggleBatchCode('${safeId}')">
            &#x25B6; Show Code (${code.split("\\n").length} lines)
        </div>
        <div class="batch-code-panel" id="batch-code-${safeId}">
            <pre class="output-panel code-output" style="max-height:250px;margin:0">${highlightedCode}</pre>
        </div>
    `;
}

function toggleBatchCode(safeId) {
    const panel = document.getElementById(`batch-code-${safeId}`);
    if (panel) panel.classList.toggle("visible");
}

function statusLabel(status) {
    const labels = {
        pending: "Pending",
        generating: "Generating...",
        rendering: "Rendering...",
        done: "Done",
        error: "Error",
    };
    return labels[status] || status;
}

// ---------------------------------------------------------------------------
// Batch Render
// ---------------------------------------------------------------------------

async function renderAllBatchResults() {
    const renderBtn = document.getElementById("btn-batch-render");
    if (renderBtn) renderBtn.disabled = true;

    const renderResults = document.getElementById("batch-render-results");
    renderResults.innerHTML = "";
    updatePipelineStatus("render", "running");

    const quality = document.getElementById("render-quality").value;

    for (const [conceptName, data] of Object.entries(state.batchResults)) {
        if (data.status !== "done" || !data.code) continue;

        const safeId = makeSafeId(conceptName);
        const sceneName = data.scene_name || "GeneratedScene";

        updateBatchCardStatus(conceptName, "rendering");

        renderResults.innerHTML += `<div class="batch-result-card" id="render-card-${safeId}">
            <div class="batch-result-header">
                <span class="concept-label">${esc(conceptName)}</span>
                <span class="batch-status rendering" id="render-status-${safeId}">Rendering...</span>
            </div>
            <div class="batch-result-body" id="render-body-${safeId}"></div>
        </div>`;

        try {
            const body = {
                stage: "render",
                code: data.code,
                scene_name: sceneName,
                video_quality: quality,
            };

            const resp = await fetch(`${API}/execute`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });

            if (!resp.ok) throw new Error("Render request failed");

            const { task_id } = await resp.json();
            const result = await waitForTaskResult(task_id);

            const renderStatusEl = document.getElementById(`render-status-${safeId}`);
            const renderBodyEl = document.getElementById(`render-body-${safeId}`);

            if (result.success && result.video_filename) {
                if (renderStatusEl) {
                    renderStatusEl.className = "batch-status done";
                    renderStatusEl.textContent = "Done";
                }
                if (renderBodyEl) {
                    renderBodyEl.innerHTML = `
                        <div class="batch-video-container">
                            <video controls src="${API}/files/video/${result.video_filename}"></video>
                        </div>
                    `;
                }
                state.batchResults[conceptName].video_filename = result.video_filename;
                updateBatchCardStatus(conceptName, "done");
            } else {
                if (renderStatusEl) {
                    renderStatusEl.className = "batch-status error";
                    renderStatusEl.textContent = `Error: ${result.error || "Unknown"}`;
                }
                updateBatchCardStatus(conceptName, "error", result.error);
            }
        } catch (err) {
            const renderStatusEl = document.getElementById(`render-status-${safeId}`);
            if (renderStatusEl) {
                renderStatusEl.className = "batch-status error";
                renderStatusEl.textContent = `Error: ${err.message}`;
            }
            updateBatchCardStatus(conceptName, "error", err.message);
        }
    }

    updatePipelineStatus("render", "completed");
    if (renderBtn) renderBtn.disabled = false;
    showToast("Batch rendering complete", "success");
}

// ---------------------------------------------------------------------------
// SSE streaming
// ---------------------------------------------------------------------------

function connectSSE(taskId, stage) {
    const es = new EventSource(`${API}/tasks/${taskId}/stream`);

    es.addEventListener("progress", (e) => {
        const progressEl = document.getElementById(`progress-text-${stage}`);
        if (progressEl) progressEl.textContent = e.data;
    });

    es.addEventListener("result", (e) => {
        try {
            const result = JSON.parse(e.data);
            handleStageResult(stage, result);
        } catch {
            handleStageResult(stage, e.data);
        }
    });

    es.addEventListener("error", (e) => {
        showToast(`Stage failed: ${e.data || "Unknown error"}`, "error");
    });

    es.addEventListener("completed", () => {
        es.close();
        setStageLoading(stage, false);
    });

    es.addEventListener("failed", () => {
        es.close();
        setStageLoading(stage, false);
        updatePipelineStatus(stage, "stale");
    });

    es.addEventListener("timeout", () => {
        es.close();
        setStageLoading(stage, false);
        updatePipelineStatus(stage, "stale");
        showToast("Task timed out", "error");
    });

    es.onerror = () => {
        es.close();
        pollTaskStatus(taskId, stage);
    };
}

async function pollTaskStatus(taskId, stage) {
    const maxPolls = 120;
    for (let i = 0; i < maxPolls; i++) {
        await sleep(2000);
        try {
            const resp = await fetch(`${API}/tasks/${taskId}`);
            if (!resp.ok) break;
            const data = await resp.json();

            if (data.progress) {
                const progressEl = document.getElementById(`progress-text-${stage}`);
                if (progressEl) progressEl.textContent = data.progress;
            }

            if (data.status === "completed" && data.result) {
                handleStageResult(stage, data.result.output);
                setStageLoading(stage, false);
                return;
            } else if (data.status === "failed") {
                showToast(data.result?.error || "Task failed", "error");
                setStageLoading(stage, false);
                updatePipelineStatus(stage, "stale");
                return;
            }
        } catch {
            break;
        }
    }
    setStageLoading(stage, false);
    updatePipelineStatus(stage, "stale");
    showToast("Task polling timed out", "error");
}

// ---------------------------------------------------------------------------
// Result handling
// ---------------------------------------------------------------------------

function handleStageResult(stage, result) {
    updatePipelineStatus(stage, "completed");

    if (stage === "extract_concepts") {
        showConceptsOutput(result);
    } else if (stage === "personalize") {
        showPersonalizedOutput(result);
    } else if (stage === "generate_animation") {
        showAnimationOutput(result);
    } else if (stage === "render") {
        showRenderOutput(result);
    }

    addHistoryEntry(stage, result);
    showToast(`${stageName(stage)} completed`, "success");
}

function showConceptsOutput(result) {
    state.outputs.concepts = result;
    const el = document.getElementById("output-extract_concepts");
    const card = document.getElementById("output-card-extract_concepts");
    card.style.display = "block";

    let html = "";
    const allConcepts = [];

    if (result.matched_concepts && result.matched_concepts.length > 0) {
        html += '<div class="concept-tree"><div class="concept-group">';
        html += `<div class="concept-group-title">Matched Concepts (${result.matched_concepts.length})</div>`;
        for (const c of result.matched_concepts) {
            html += `<div class="concept-item">
                <span class="concept-id">${esc(c.concept_id)}</span>
                <span>${esc(c.name)}</span>
                <span class="confidence">${Math.round((c.confidence || 0) * 100)}%</span>
            </div>`;
            allConcepts.push(c);
        }
        html += "</div>";

        if (result.new_concepts && result.new_concepts.length > 0) {
            html += '<div class="concept-group">';
            html += `<div class="concept-group-title">New Concepts (${result.new_concepts.length})</div>`;
            for (const c of result.new_concepts) {
                html += `<div class="concept-item">
                    <span class="concept-id">${esc(c.suggested_id)}</span>
                    <span>${esc(c.name)} - ${esc(c.description || "")}</span>
                </div>`;
                allConcepts.push({ ...c, concept_id: c.suggested_id });
            }
            html += "</div>";
        }
        html += "</div>";
    } else {
        html = '<div style="color: var(--text-muted)">No concepts found</div>';
    }

    if (result.summary) {
        html += `<div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border); color: var(--text-secondary)">
            <strong>Summary:</strong> ${esc(result.summary)}
        </div>`;
    }

    el.innerHTML = html;
    showStats("extract_concepts", result);

    // Populate concept checklist in Stage 4 for batch generation
    renderConceptChecklist(allConcepts);
}

function showPersonalizedOutput(result) {
    const content = result.personalized_content || "";
    state.outputs.personalized = content;
    const el = document.getElementById("output-personalize");
    const card = document.getElementById("output-card-personalize");
    card.style.display = "block";

    if (typeof marked !== "undefined") {
        el.innerHTML = marked.parse(content);
    } else {
        el.textContent = content;
    }
    showStats("personalize", result);
}

function showAnimationOutput(result) {
    const code = result.code || "";
    state.outputs.animation_code = code;
    state.outputs.scene_name = result.scene_name || "GeneratedScene";

    const el = document.getElementById("output-generate_animation");
    const card = document.getElementById("output-card-generate_animation");
    card.style.display = "block";

    if (typeof hljs !== "undefined") {
        el.innerHTML = hljs.highlight(code, { language: "python" }).value;
    } else {
        el.textContent = code;
    }

    // Also populate the render section
    document.getElementById("render-code").value = code;
    document.getElementById("render-scene-name").textContent =
        `Scene: ${state.outputs.scene_name}`;

    if (result.validation && !result.validation.is_valid) {
        const errs = (result.validation.errors || []).join(", ");
        showToast(`Validation issues: ${errs}`, "warning");
    }

    showStats("generate_animation", result);
}

function showRenderOutput(result) {
    const container = document.getElementById("video-output");

    if (result.success && result.video_filename) {
        const video = document.getElementById("rendered-video");
        video.src = `${API}/files/video/${result.video_filename}`;
        container.style.display = "block";
        video.load();

        const statsEl = document.getElementById("stats-render");
        statsEl.innerHTML = `
            <span class="stat">Render time: <span class="stat-value">${(result.render_time_ms / 1000).toFixed(1)}s</span></span>
        `;
    } else {
        container.style.display = "none";
        showToast(`Render failed: ${result.error || "Unknown error"}`, "error");
    }
}

function showStats(stage, result) {
    const el = document.getElementById(`stats-${stage}`);
    if (!el) return;

    const parts = [];
    if (result.duration_ms) {
        parts.push(
            `<span class="stat">Duration: <span class="stat-value">${(result.duration_ms / 1000).toFixed(1)}s</span></span>`
        );
    }
    if (result.tokens_used) {
        const inp = result.tokens_used.input_tokens || result.tokens_used.prompt_tokens || 0;
        const out = result.tokens_used.output_tokens || result.tokens_used.completion_tokens || 0;
        if (inp || out) {
            parts.push(
                `<span class="stat">Tokens: <span class="stat-value">${inp.toLocaleString()} in / ${out.toLocaleString()} out</span></span>`
            );
        }
    }
    if (result.model_used) {
        parts.push(
            `<span class="stat">Model: <span class="stat-value">${esc(result.model_used)}</span></span>`
        );
    }
    el.innerHTML = parts.join("");
}

// ---------------------------------------------------------------------------
// History
// ---------------------------------------------------------------------------

function addHistoryEntry(stage, result) {
    const entry = {
        stage,
        success: !result.error,
        timestamp: new Date().toLocaleTimeString(),
        label: stageName(stage),
    };
    state.history.unshift(entry);
    renderHistory();
}

function renderHistory() {
    const list = document.getElementById("history-list");
    if (state.history.length === 0) {
        list.innerHTML = '<div style="padding: 4px 0; font-size: 13px; color: var(--text-muted);">No runs yet</div>';
        return;
    }
    list.innerHTML = state.history
        .slice(0, 20)
        .map(
            (h) => `
        <div class="history-item">
            <span class="status-dot ${h.success ? "success" : "error"}"></span>
            <span>${esc(h.label)}</span>
            <span style="margin-left:auto; font-size:11px; color:var(--text-muted)">${h.timestamp}</span>
        </div>
    `
        )
        .join("");
}

// ---------------------------------------------------------------------------
// UI Helpers
// ---------------------------------------------------------------------------

function setStageLoading(stage, loading) {
    const progress = document.getElementById(`progress-${stage}`);
    const btn = document.getElementById(`btn-exec-${stage}`);

    if (progress) {
        progress.classList.toggle("visible", loading);
    }
    if (btn) {
        btn.disabled = loading;
    }
}

function copyCode() {
    const code = state.outputs.animation_code;
    if (code) {
        navigator.clipboard.writeText(code).then(() => {
            showToast("Code copied to clipboard", "success");
        });
    }
}

function stageName(stage) {
    const names = {
        upload: "Upload",
        extract_concepts: "Extract Concepts",
        personalize: "Personalize",
        generate_animation: "Generate Animation",
        render: "Render Video",
        parse_examples: "Parse Examples",
    };
    return names[stage] || stage;
}

function esc(str) {
    const div = document.createElement("div");
    div.textContent = str || "";
    return div.innerHTML;
}

function makeSafeId(str) {
    return (str || "").replace(/[^a-zA-Z0-9]/g, "_");
}

function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

// ---------------------------------------------------------------------------
// LLM Settings
// ---------------------------------------------------------------------------

function initLLMSettingsUI() {
    const tempSlider = document.getElementById("llm-temperature");
    const tempValue = document.getElementById("llm-temperature-value");
    const maxTokensSelect = document.getElementById("llm-max-tokens");
    const modelDisplay = document.getElementById("llm-model-display");
    const providerDisplay = document.getElementById("llm-provider-display");

    if (tempSlider) {
        tempSlider.value = state.llmSettings.temperature;
        tempValue.textContent = state.llmSettings.temperature.toFixed(2);
    }
    if (maxTokensSelect) {
        maxTokensSelect.value = String(state.llmSettings.maxTokens);
    }
    if (modelDisplay) {
        modelDisplay.textContent = state.config.model || "unknown";
    }
    if (providerDisplay) {
        providerDisplay.textContent = state.config.llm_provider || "unknown";
    }
    updateLLMSettingsSummary();
}

function toggleLLMSettings() {
    const panel = document.getElementById("llm-settings-panel");
    const chevron = document.getElementById("llm-settings-chevron");
    const isVisible = panel.classList.contains("visible");
    panel.classList.toggle("visible", !isVisible);
    chevron.classList.toggle("expanded", !isVisible);
}

function onTemperatureChange() {
    const slider = document.getElementById("llm-temperature");
    const display = document.getElementById("llm-temperature-value");
    const value = parseFloat(slider.value);
    state.llmSettings.temperature = value;
    display.textContent = value.toFixed(2);
    updateLLMSettingsSummary();
}

function onMaxTokensChange() {
    const select = document.getElementById("llm-max-tokens");
    state.llmSettings.maxTokens = parseInt(select.value, 10);
    updateLLMSettingsSummary();
}

function updateLLMSettingsSummary() {
    const el = document.getElementById("llm-settings-summary");
    if (el) {
        el.textContent = `temp=${state.llmSettings.temperature.toFixed(2)}, tokens=${state.llmSettings.maxTokens.toLocaleString()}`;
    }
}

// ---------------------------------------------------------------------------
// Toast notifications
// ---------------------------------------------------------------------------

function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transition = "opacity 0.3s";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
