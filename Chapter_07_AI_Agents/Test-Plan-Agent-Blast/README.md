# 🧪 Test Plan Creator from a Jira ID

🚀 **Live app:** [test-plan-creator-ai-agent.streamlit.app](https://test-plan-creator-ai-agent.streamlit.app)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://test-plan-creator-ai-agent.streamlit.app)

A simple UI that turns a prompt like *"Fetch this Jira and create a test plan"* into a
complete, structured Test Plan. It fetches the Jira ticket automatically, builds a
**deterministic plan skeleton** (scenarios, cases, requirement traceability), then uses
**GROQ** (`groq.com`, default model `openai/gpt-oss-120b`) to enrich the prose.

Built with the **B.L.A.S.T.** framework (3-layer architecture: `architecture/` SOPs →
`app.py`/`orchestrator.py` navigation → `tools/` deterministic modules).

## Features

- **Generate page** — paste a prompt, the Jira key is auto-detected (`PROJ-123`), click
  Generate, get a stylized markdown Test Plan with a download button.
- **Settings page** — configure:
  - Jira base URL, email, API token
  - GROQ API key + model
  - **Test Jira Connection** and **Test GROQ Connection** (GROQ test lists live models)
- **Demo page** — offline demo against the bundled `DEMO-101` fixture, no credentials required.
- Resilient: if GROQ fails, the deterministic engine still returns a complete, validated plan.

## Setup

```bash
# 1. create venv + install
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

# 2. optional: copy .env.example -> .env to seed defaults
# 3. run
streamlit run app.py
```

Then open the printed URL (default http://localhost:8501).

> **Port troubleshooting:** if the app does not come up on 8501 (some Windows
> terminals/IDE runners interrupt the default port), run it on an explicit port
> instead:
> ```bash
> streamlit run app.py --server.port 8502
> ```
> and open http://localhost:8502.

## Where credentials live

- Credentials live in **`.env`** (git-ignored) — the single source of truth.
- Click **Save** in Settings to write them there (or edit `.env` directly; see `.env.example`).
- Settings shows whether a Jira token / GROQ key is currently saved, lets you replace it,
  and has a **clear** checkbox to remove it.
- Never commit `.env`.

## Configuration notes

- **Jira**: Cloud (v3) or Server/DC (v2) is auto-detected. Requires an email + API token
  (Cloud) or username + password (Server).
- **Acceptance Criteria** are auto-discovered: custom field → ADF/wiki heading → description.
  If your instance stores them in a specific custom field not auto-detected, tell us and we
  can extend `tools/jira_client.py` (update `architecture/SOP-01` first per the Golden Rule).
- **GROQ model**: default `openai/gpt-oss-120b`. Use **Test GROQ Connection** to list the
  models your key can access and pick one.

## Project layout

```
app.py                     # Streamlit UI (Settings + Generate + Demo)
architecture/SOP-*.md      # Layer 1: technical SOPs
tools/                     # Layer 3: deterministic modules
  config_store.py          # settings persistence (.env single store, legacy migration)
  jira_client.py           # fetch + normalize issue (ADF/wiki/plain), test connection
  groq_client.py           # GROQ chat (JSON mode) + test connection (list models)
  plan_engine.py           # deterministic skeleton + LLM merge + validate + markdown
  orchestrator.py          # Layer 2 nav: run(key) -> plan; CLI: python -m tools.orchestrator PROJ-123
  fixtures/sample_issue.json
task_plan.md findings.md progress.md LLM.md   # BLAST project memory (Protocol 0)
```
