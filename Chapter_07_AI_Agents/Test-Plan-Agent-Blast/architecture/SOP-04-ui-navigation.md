# SOP-04 — UI & Navigation (Streamlit App + Orchestrator)

**Layer:** 2 (Navigation) · **Modules:** `app.py`, `tools/orchestrator.py` · **Status:** Implemented

## Goal
Provide a **simple UI** where the user gives a prompt like *"Fetch this Jira and create a test plan"*, and the app automatically fetches the Jira ticket and generates the test plan. Also provide a **Settings** page to configure Jira + Groq credentials with live connection tests.

## Pages

### 1. Settings page
- Jira section: `base_url`, `email`, `api_token` (password), **Test Jira Connection**.
- Groq section: `api_key` (password), `model` (text; prefilled `openai/gpt-oss-120b`), **Test Groq Connection** (lists live models on success).
- **Save Settings** → writes the local `.env` (single source of truth, git-ignored).
  The form shows whether a Jira token / GROQ key is saved, allows replacement, and offers
  a **clear** checkbox to remove a saved secret. The status line refreshes after saving.

### 2. Generate page
- Free-text prompt, e.g. *"Fetch this Jira and create a test plan."*
- Issue key field. If the prompt contains a Jira key pattern (`[A-Z]+-\d+`), it is auto-extracted; the field lets the user override.
- **Prompt parsing (enhanced):**
  1. Extract a Jira key (`PROJ-123`) anywhere in the prompt.
  2. If none, but the prompt names an issue *title* (or a key-like word), allow a **by-title issue lookup** in Settings (falls back to an error that says "I couldn't find a Jira key in your prompt").
  3. Only a key actually fetches deterministically — the LLM never guesses which ticket to fetch.
- **Generate Test Plan** button:
  1. Load settings; if missing → clear error ("go to Settings").
  2. Orchestrator: fetch → normalize → skeleton → Groq prose → validate → markdown.
  3. Render markdown in a styled container, offer **Download .md**.
  4. Any failure (auth/not_found/network) renders a clear error and does not fabricate a plan.

## Orchestrator behavior (`tools/orchestrator.py`)
- `run(issue_key, settings)` → returns `test_plan` dict + `error` if any.
- If Groq fails, returns the deterministic skeleton plan flagged `generation.mode = "fallback"` (never silently empty).
- CLI: `python -m tools.orchestrator PROJ-123` for Trigger-phase automation.

## Golden Rule
If UI/navigation flow changes, update this SOP first, then the code.
