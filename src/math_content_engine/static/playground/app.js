/* ================================================================
   Math Content Playground — Frontend Application
   ================================================================ */

const API = "/api/v1/playground";

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

const state = {
    textbookContent: "",
    currentStage: "upload",
    interest: null,
    config: {},
    // LLM settings (user-tunable)
    llmSettings: {
        temperature: 0.7,
        maxTokens: 4096,
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
    // Run history
    history: [],
};

// ---------------------------------------------------------------------------
// Initialization
// ---------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", async () => {
    await loadConfig();
    // Configure marked for markdown rendering
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

        // Update header
        document.getElementById("config-provider").textContent =
            state.config.llm_provider || "?";
        document.getElementById("config-model").textContent =
            state.config.model || "";

        // Initialize LLM settings from server config
        state.llmSettings.temperature = state.config.temperature || 0.7;
        state.llmSettings.maxTokens = state.config.max_tokens || 4096;
        initLLMSettingsUI();

        // Populate interest dropdowns
        populateInterests(state.config.available_interests || []);
    } catch (err) {
        showToast(`Failed to load config: ${err.message}`, "error");
    }
}

function populateInterests(interests) {
    const selects = [
        document.getElementById("interest-select"),
        document.getElementById("personalize-interest"),
    ];
    for (const sel of selects) {
        // Keep the first option
        while (sel.options.length > 1) sel.remove(1);
        for (const name of interests) {
            const opt = document.createElement("option");
            opt.value = name;
            opt.textContent = name.charAt(0).toUpperCase() + name.slice(1);
            sel.appendChild(opt);
        }
    }
}

// ---------------------------------------------------------------------------
// Navigation
// ---------------------------------------------------------------------------

function switchStage(stage) {
    state.currentStage = stage;

    // Update sidebar
    document.querySelectorAll(".sidebar-item").forEach((el) => {
        el.classList.toggle("active", el.dataset.stage === stage);
    });

    // Update panels
    document.querySelectorAll(".stage-panel").forEach((el) => {
        el.classList.toggle("active", el.id === `stage-${stage}`);
    });
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
    } else {
        stats.textContent = "";
    }
}

function onInterestChange() {
    const sel = document.getElementById("interest-select");
    state.interest = sel.value || null;
    // Sync the personalize interest dropdown
    document.getElementById("personalize-interest").value = state.interest || "";
}

function onPersonalizeInterestChange() {
    const sel = document.getElementById("personalize-interest");
    state.interest = sel.value || null;
    document.getElementById("interest-select").value = state.interest || "";
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

**Verification:** 7 + 5 = 12 \\u2713

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

**Verification:** 2(4) + 3 = 8 + 3 = 11 \\u2713

## Practice Problems

1. Solve: x - 8 = 15
2. Solve: 5x = 45
3. Solve: 4x + 7 = 31
4. Solve: 2x - 9 = 13
`;
    document.getElementById("textbook-input").value = sample;
    state.textbookContent = sample;
    onTextbookInput();
    showToast("Sample textbook loaded", "info");
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

        // Store defaults
        state.defaultPrompts[stage] = {
            system: data.system_prompt,
            user: data.user_prompt,
        };

        // Populate textareas
        document.getElementById(`prompt-${stage}-system`).value = data.system_prompt;
        document.getElementById(`prompt-${stage}-user`).value = data.user_prompt;

        showToast("Prompts loaded", "success");
    } catch (err) {
        showToast(`Error: ${err.message}`, "error");
    }
}

function buildPreviewRequest(stage) {
    const req = { stage };

    if (stage === "personalize") {
        if (!state.textbookContent) {
            showToast("Upload textbook content first (step 1)", "error");
            return null;
        }
        if (!state.interest) {
            showToast("Select an interest first", "error");
            return null;
        }
        req.textbook_content = state.textbookContent;
        req.interest = state.interest;
    } else if (stage === "extract_concepts") {
        if (!state.textbookContent) {
            showToast("Upload textbook content first (step 1)", "error");
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
        if (state.interest) req.interest = state.interest;
        // Student profile fields
        const studentName = document.getElementById("anim-student-name").value || "";
        const preferredAddress = document.getElementById("anim-preferred-address").value || "";
        const favoriteFigure = document.getElementById("anim-favorite-figure").value || "";
        const favoriteTeam = document.getElementById("anim-favorite-team").value || "";
        if (studentName) req.student_name = studentName;
        if (preferredAddress) req.preferred_address = preferredAddress;
        if (favoriteFigure) req.favorite_figure = favoriteFigure;
        if (favoriteTeam) req.favorite_team = favoriteTeam;
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
            return;
        }
        const { task_id } = await resp.json();
        connectSSE(task_id, stage);
    } catch (err) {
        showToast(`Error: ${err.message}`, "error");
        setStageLoading(stage, false);
    }
}

function buildExecuteRequest(stage) {
    const req = { stage };

    // Always include LLM parameter overrides
    req.temperature = state.llmSettings.temperature;
    req.max_tokens = state.llmSettings.maxTokens;

    // Check for prompt overrides
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

    if (stage === "personalize") {
        if (!state.textbookContent) {
            showToast("Upload textbook content first", "error");
            return null;
        }
        if (!state.interest) {
            showToast("Select an interest first", "error");
            return null;
        }
        req.textbook_content = state.textbookContent;
        req.interest = state.interest;
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
        if (state.interest) req.interest = state.interest;
        // Student profile fields
        const studentName = document.getElementById("anim-student-name").value || "";
        const preferredAddress = document.getElementById("anim-preferred-address").value || "";
        const favoriteFigure = document.getElementById("anim-favorite-figure").value || "";
        const favoriteTeam = document.getElementById("anim-favorite-team").value || "";
        if (studentName) req.student_name = studentName;
        if (preferredAddress) req.preferred_address = preferredAddress;
        if (favoriteFigure) req.favorite_figure = favoriteFigure;
        if (favoriteTeam) req.favorite_team = favoriteTeam;
    }
    return req;
}

async function executeRender() {
    const code = document.getElementById("render-code").value;
    if (!code) {
        showToast("No code to render. Generate animation first (step 4)", "error");
        return;
    }

    // Extract scene name from code
    const match = code.match(/class\s+(\w+)\s*\(\s*Scene\s*\)/);
    const sceneName = match ? match[1] : "GeneratedScene";

    const body = {
        stage: "render",
        code: code,
        scene_name: sceneName,
        video_quality: document.getElementById("render-quality").value,
    };

    setStageLoading("render", true);

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
            return;
        }
        const { task_id } = await resp.json();
        connectSSE(task_id, "render");
    } catch (err) {
        showToast(`Error: ${err.message}`, "error");
        setStageLoading("render", false);
    }
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
    });

    es.addEventListener("timeout", () => {
        es.close();
        setStageLoading(stage, false);
        showToast("Task timed out", "error");
    });

    es.onerror = () => {
        // EventSource auto-reconnects, but if we get repeated errors, close.
        // Use polling fallback instead.
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
                return;
            }
        } catch {
            break;
        }
    }
    setStageLoading(stage, false);
    showToast("Task polling timed out", "error");
}

// ---------------------------------------------------------------------------
// Result handling
// ---------------------------------------------------------------------------

function handleStageResult(stage, result) {
    if (stage === "extract_concepts") {
        showConceptsOutput(result);
    } else if (stage === "personalize") {
        showPersonalizedOutput(result);
    } else if (stage === "generate_animation") {
        showAnimationOutput(result);
    } else if (stage === "render") {
        showRenderOutput(result);
    }

    // Add to history
    addHistoryEntry(stage, result);
    showToast(`${stageName(stage)} completed`, "success");
}

function showConceptsOutput(result) {
    state.outputs.concepts = result;
    const el = document.getElementById("output-extract_concepts");
    const card = document.getElementById("output-card-extract_concepts");
    card.style.display = "block";

    let html = "";
    if (result.matched_concepts && result.matched_concepts.length > 0) {
        html += '<div class="concept-tree"><div class="concept-group">';
        html += `<div class="concept-group-title">Matched Concepts (${result.matched_concepts.length})</div>`;
        for (const c of result.matched_concepts) {
            html += `<div class="concept-item">
                <span class="concept-id">${esc(c.concept_id)}</span>
                <span>${esc(c.name)}</span>
                <span class="confidence">${Math.round((c.confidence || 0) * 100)}%</span>
            </div>`;
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

    // Highlight Python code
    if (typeof hljs !== "undefined") {
        el.innerHTML = hljs.highlight(code, { language: "python" }).value;
    } else {
        el.textContent = code;
    }

    // Also populate the render tab
    document.getElementById("render-code").value = code;
    document.getElementById("render-scene-name").textContent =
        `Scene: ${state.outputs.scene_name}`;

    // Show validation warnings
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
        list.innerHTML = '<div style="padding: 8px 16px; font-size: 13px; color: var(--text-muted);">No runs yet</div>';
        return;
    }
    list.innerHTML = state.history
        .slice(0, 20)
        .map(
            (h, i) => `
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
