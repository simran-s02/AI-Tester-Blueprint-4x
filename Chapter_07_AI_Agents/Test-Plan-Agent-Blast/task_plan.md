# 📋 Task Plan — Test Plan Creator from a Jira ID

**Protocol:** 0 — Initialization (B.L.A.S.T.)
**Project Folder:** `Chapter_07_AI_Agents/Test-Plan-Agent-Blast/`
**Created:** 2026-09-05 16:20 (UTC+8 local)
**Owner:** System Pilot (AI Agent)
**Phase Status:** Phase 1 ✅ | Phase 2 ✅ | Phase 3 ✅ | Phase 4 ✅ | Phase 5 🟡

---

## 🎯 North Star (Primary Goal)

> A **simple UI** where the user gives a prompt like *"Fetch this Jira and create a test plan."* The app then automatically fetches the Jira ticket and generates a complete, structured **Test Plan** document — using a **Groq** LLM (open 120B-parameter model, e.g. `openai/gpt-oss-120b`) for content generation.
> **Session 3:** The same prompt now works **without a key and without credentials** — the app falls back to a bundled demo issue, and can also look issues up **by title** (JQL).
> **Session 5:** Output upgraded to the **STLC review-ready draft model** (schema v2) from `Chapter_02/STLC_SKILLS` — gap analysis + questions for the author, P0/P1/P2 scenario priorities with type tags, and a HUMAN REVIEW GATE (plans ship as DRAFT).

---

## ✅ Discovery Answers (from user — Phase 1)

| Question | Answer |
|----------|--------|
| **North Star** | Simple UI → user types "Fetch this Jira and create a test plan" → app fetches Jira + generates test plan automatically |
| **Integrations** | **Jira** (REST API) + **GROQ** (`groq.com`, open GPT-120B class model) |
| **Source of Truth** | Jira ticket via Jira REST API (Cloud v3; Server v2 fallback) |
| **Delivery Payload** | Rendered Test Plan in the UI (downloadable `.md`) |
| **Behavioral Rules** | Deterministic pipeline (fetch → normalize → build skeleton → LLM prose → validate → deliver); LLM only fills prose, never makes business decisions |
| **Settings UI** | Allow Jira API URL, email ID, API token + **Test Connection** for Jira and Groq + Groq API key, model selection |
| **Extra** | User picks which Jira ID / issue to fetch in the Generate page |

---

## ✅ Project Goals

| # | Goal | Status | Notes |
|---|------|--------|-------|
| G1 | Simple UI (Streamlit) — Generate page + Settings page | ✅ Done | `app.py` |
| G2 | Settings: Jira URL/email/token + Groq key/model, saved locally | ✅ Done | `.env` via `tools/config_store.py` |
| G3 | Test Connection buttons for Jira and Groq | ✅ Done | `tools/jira_client.py` / `tools/groq_client.py` |
| G4 | Parse issue: summary, description, acceptance criteria, type, priority, labels | ✅ Done | ADF + wiki + plain-text handling |
| G5 | Auto-generate test plan with scenarios/cases/coverage | ✅ Done | deterministic skeleton + Groq prose |
| G6 | Professional, stylized Test Plan delivery (`.md` + UI) | ✅ Done | Phase 4 Stylize |
| G7 | Deterministic + traceable plan structure | ✅ Done | Golden Rule enforced |
| G8 | Follow B.L.A.S.T. 3-layer architecture (SOPs / nav / tools) | ✅ Done | architecture/ + tools/ |
| G9 | Run locally | ✅ Done | Streamlit |

---

## ✅ Checklist — Protocol 0 (Initialization)

- [x] Read `BLAST.md` master system prompt
- [x] Identify current phase: Protocol 0 — Initialization
- [x] **Create `task_plan.md`** (this file) — phases, goals, checklists
- [x] **Create `findings.md`** — research, discoveries, constraints
- [x] **Create `progress.md`** — timestamped log of work
- [x] **Create `LLM.md`** — Project Constitution: schemas, rules, invariants
- [x] Define Input/Output JSON Schema (in `LLM.md`)
- [x] Approve blueprint (user gave full scope + Go) ✅ **HALT LIFTED**

---

## ✅ Checklist — Phase 1: B — Blueprint (Vision & Logic)

- [x] Answer Discovery Questions (confirmed with user)
- [x] Define the JSON Data Schema for Input and Output (`LLM.md`)
- [x] Research: Jira REST API + Groq API (`openai/gpt-oss-120b` model via Groq)
- [x] Define behavioral rules (tone, constraints, "Do Not" rules)
- [x] Approve blueprint → user said **"do Phase 1–4 in one go"**

---

## ✅ Checklist — Phase 2: L — Link (Connectivity)

- [x] Design Link layer: `.env` (single store) + `tools/jira_client.py` + `tools/groq_client.py`
- [x] Jira REST handshake: `GET /rest/api/3/myself` (v3) / `GET /rest/api/2/myself` (v2)
- [x] Groq handshake: `GET https://api.groq.com/openai/v1/models`
- [x] If Link is broken → UI shows error, does not proceed to full logic

---

## ✅ Checklist — Phase 3: A — Architect (3-Layer Build)

- [x] Write Technical SOPs in `architecture/` (goals, inputs, tool logic, edge cases)
- [x] Navigation layer (thin orchestrator): route issue data → parser → generator (`tools/orchestrator.py`)
- [x] Build `tools/` deterministic Python scripts (atomic, testable)
- [x] Store tokens in `.env` (never in code) ✅
- [x] Use `.tmp/` for all intermediate file operations
- [x] Update SOP **before** updating code when logic changes (Golden Rule)

---

## ✅ Checklist — Phase 4: S — Stylize (Refinement & UI)

- [x] Format the Test Plan output for professional delivery (`.md` with tables + traceability)
- [x] UI: Streamlit Generate page + Settings page
- [x] Present stylized results to user for feedback (running app)

---

## ✅ Checklist — Phase 5: T — Trigger (Automation) 🟡 Pending

- [ ] Add scheduled/trigger mode (e.g. watch a Jira status, or CLI `python -m tools.orchestrator PROJ-123`)
- [ ] Optional webhook/status-trigger for automatic generation
- [ ] End-to-end run with real Jira ID + real Groq key
- [ ] Self-healing / retries on transient API errors

---

## 📦 Deliverables

| Deliverable | Description | Status |
|-------------|-------------|--------|
| `task_plan.md` | Goals, checklists, milestones | ✅ |
| `findings.md` | Research + API details | ✅ |
| `progress.md` | Work log with timestamps | ✅ |
| `LLM.md` | Schemas, rules, architecture invariants | ✅ |
| `architecture/*.md` | Technical SOPs | ✅ |
| `tools/*.py` | Deterministic Python modules | ✅ |
| `app.py` | Streamlit UI (Settings + Generate) | ✅ |
| `README.md` | Run instructions | ✅ |
| `.env.example` | Template for credentials | ✅ |

---

## 🚧 Constraints / Do-Not Rules

- **Do not** hardcode secrets — `.env` only (git-ignored, single source of truth).
- **Do not** let LLM make business decisions — deterministic skeleton first.
- **Do not** proceed past a broken Link (connection test fails → stop).
- **Do not** guess field mappings — user supplies Jira field info in Settings if needed.
- **Scope:** use **only** the `Chapter_07_AI_Agents/Test-Plan-Agent-Blast/` folder for this project.
