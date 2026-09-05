# 📈 Progress Log — Test Plan Creator from a Jira ID

> **Rule:** Every work session appends a timestamped entry: what was done, errors encountered, results, next step.
> Timezone: UTC+8 (local). Format: `HH:MM` — `Action | Result | Error (if any) | Next`.

---

## Session 1 — Protocol 0: Initialization

### 16:20 — Session start
- **Action:** Read `BLAST.md`, `Prompt_Used.md`; listed `Chapter_07_AI_Agents/` contents.
- **Result:** Confirmed Protocol 0 (Initialization) is the current step. Folder contains only `BLAST.md` + `Prompt_Used.md`. Objective confirmed: **Test Plan Creator from a Jira ID**.
- **Error:** None.
- **Next:** Create the 4 project memory files.

### 16:21 — Created `task_plan.md`
- **Action:** Defined North Star, goals G1–G7, checklists for Protocols 0→5, deliverables, constraints.
- **Result:** Blueprint skeleton for the whole project (phases, goals, checklists) is now tracked. ✅
- **Error:** None.
- **Next:** Create `findings.md`.

### 16:22 — Created `findings.md`
- **Action:** Researched the Jira REST API surface from knowledge: auth methods (PAT vs Basic), v3 endpoints (`/myself`, `/issue/{key}`, `/search`), ADF vs wiki markup, acceptance-criteria field discovery, issuelinks usage. Documented curl examples (Windows `curl.exe` + Unix) and expected JSON shape.
- **Result:** Findings + 6 open Discovery questions documented. ⚠️ Key discovery: acceptance criteria location varies per Jira instance — must not be assumed.
- **Error:** None (no live API calls made yet — intentionally halted by Protocol 0 until credentials/blueprint approved).
- **Next:** Create `progress.md` (this file).

### 16:23 — Created `progress.md` (this file)
- **Action:** Started timestamped work log for the project.
- **Result:** Logging discipline established — every future action gets a time + result + error entry.
- **Error:** None.
- **Next:** Create `LLM.md` (Project Constitution: schemas + rules + invariants).

### 16:24 — Created `LLM.md`
- **Action:** Defined Input/Output JSON schemas, behavioral rules, and the 3-layer architectural invariants for the project.
- **Result:** Project Constitution documented → Protocol 0 checklist items complete.
- **Error:** None.
- **Next:** ⛔ **HALT** — present blueprint to user, ask the 5 Discovery Questions (North Star / Integrations / Source of Truth / Delivery / Behavioral Rules) before any `tools/` code.

---

## Session 2 — Phases 1–4 + local run (one go)

### 16:45 — Discovery answered + scope confirmed
- **Action:** User answered the 5 Discovery Questions in one message and approved moving through Phases 1–4: simple UI (Streamlit), Jira + **GROQ** integrations, Settings page with Test Connection for both, LLM = open 120B GPT via Groq (`openai/gpt-oss-120b`).
- **Result:** Protocol 0 HALT lifted. North Star locked.
- **Error:** None.
- **Next:** Phase 1 Blueprint doc updates.

### 16:46 — Phase 1 doc updates
- **Action:** Rewrote `task_plan.md` (goals/checklists/Discovery table), updated `findings.md` (Groq API research, tooling decision, resolved questions), rewrote `LLM.md` (APPROVED status, Settings schema, `generation` field, resilience rules 9–10).
- **Result:** Blueprint approved & recorded. ✅
- **Error:** None.
- **Next:** Scaffold + install deps (Phase 2).

### 16:47 — Phase 2 scaffold
- **Action:** Created `requirements.txt`, `.env.example`, `.gitignore`, `README.md`, and directories `architecture/`, `tools/`, `.tmp/`, `output/`.
- **Result:** Project skeleton in place.
- **Error:** None.
- **Next:** Create venv + install.

### 16:50 — venv + deps
- **Action:** `python -m venv .venv`; upgraded pip; `pip install -r requirements.txt` (streamlit 1.63, requests, python-dotenv).
- **Result:** All dependencies installed in `.venv`. ✅
- **Error:** None.
- **Next:** Write architecture SOPs (docs before code).

### 16:52 — Phase 3a: SOPs
- **Action:** Wrote `architecture/SOP-01-jira-fetch.md`, `SOP-02-groq-llm.md`, `SOP-03-plan-engine.md`, `SOP-04-ui-navigation.md` (each: goal, input, behavior, edge cases, Golden Rule).
- **Result:** Layer-1 docs precede code per B.L.A.S.T.
- **Error:** None.
- **Next:** Build `tools/` modules.

### 17:00 — Phase 3b: tools layer
- **Action:** Wrote `tools/__init__.py`, `config_store.py` (`.app_settings.json` + `.env` merge/mask), `jira_client.py` (v3/v2 detection, ADF/wiki/plain→md normalize, AC extraction, links), `groq_client.py` (models test + JSON chat), `plan_engine.py` (deterministic skeleton, LLM merge, validate, markdown), `orchestrator.py` (nav + CLI), `fixtures/sample_issue.json`.
- **Result:** All modules compiled clean (`py_compile` passed).
- **Error:** None.
- **Next:** Build the Streamlit UI.

### 17:10 — Phase 3c + 4: UI
- **Action:** Wrote `app.py` with 3 pages: **Generate** (prompt → auto-detect Jira key → run pipeline → styled markdown + download), **Settings** (Jira URL/email/token, Groq key/model, Test Connection buttons that hit live `/myself` and `/models`), **Demo (offline)** (fixture, no creds). README run instructions added.
- **Result:** UI complete.
- **Error:** None.
- **Next:** Smoke-test the pipeline.

### 17:18 — Smoke test (offline fixture)
- **Action:** Normalized `DEMO-101` fixture → built skeleton → validated → rendered markdown.
- **Result:** 3 acceptance criteria extracted from ADF; 5 scenarios / 5 test cases; traceability matrix complete; **validation errors = []**; markdown rendered with headers/tables. ✅
- **Error (fixed):** **RecursionError** in ADF renderer — `listItem` branch re-called `_adf_text` on itself → rewrote with `_adf_list` walker (bounded depth). Then **TypeError** — `re.search` got a tuple pattern → replaced with compiled alternation regex. Both fixed and re-verified.
- **Next:** Edge-case tests.

### 17:21 — Edge-case tests
- **Action:** Ran no-creds, blank-key, Groq no-key, Jira bad-key, wiki-markup→md cases.
- **Result:** All returned clean, typed errors (`config`, `bad_key`) — no crashes. ✅
- **Error:** None.
- **Next:** Run the app.

### 17:23 — Local run
- **Action:** `streamlit run app.py --server.headless true --server.port 8501` in background.
- **Result:** Health endpoint `/_stcore/health` → **ok**; root page → **HTTP 200**. AppTest across all 3 pages (Generate/Settings/Demo + demo button click) → **no exceptions**. ✅
- **Error:** None.
- **Next:** Stop server, finalize docs.

### 17:30 — Cleanup + docs finalize
- **Action:** Stopped dev server (task `s0wns9vg`); removed temp `task_plan_checklist.md`; updated `progress.md`; synced `task_plan.md` / `findings.md` / `LLM.md` statuses.
- **Result:** Phases 1–4 complete; project runs locally. Phase 5 (Trigger) remains pending by design.
- **Error:** None.
- **Next:** User opens the app, adds real Jira + Groq credentials in Settings, runs Generate on a real ticket.

---

## Session 3 — Prompt-robustness + demo-mode UI flow (no credentials yet)

### 17:45 — Checked for credentials
- **Action:** Searched the workspace + env vars for Jira/Groq credentials (`.app_settings.json`, `.env`, env vars).
- **Result:** No credentials exist yet (only an unrelated Chapter_03 `.env`). Live API run not possible; verified the folder referenced is a **LinkedIn/Medium content skill** (Testing Academy voice), not needed for this execution.
- **Error:** None.
- **Next:** Make the Generate flow robust for the exact prompt phrasing and prove the full UI path offline.

### 17:46 — Golden Rule: updated SOP-04 first
- **Action:** Documented enhanced prompt parsing in `architecture/SOP-04-ui-navigation.md` (key extraction → by-title lookup → demo fallback).
- **Result:** SOP reflects the intended behavior before code changes.
- **Error:** None.
- **Next:** Implement.

### 17:47 — Code: demo mode + by-title lookup
- **Action:** Added `issue_lookup_by` + `demo_mode` to settings (`config_store.py`); added `fetch_issue_by_title()` (JQL `summary ~`) to `jira_client.py`; refactored `app.py` Generate page to:
  - run **demo mode** against the bundled fixture when no Jira is configured (exact "Fetch this Jira and create a test plan" prompt now works with no key),
  - auto-detect keys, do **by-title JQL lookup** when Settings is set to title mode,
  - show a clear "Demo mode" banner on generated output.
- **Result:** `py_compile` clean; shared `_build_demo_plan()` helper used by Generate + Demo pages.
- **Error:** None.
- **Next:** Test.

### 17:51–17:59 — UI flow tests (AppTest)
- **Action:** Simulated the full UI: Generate page (demo mode, empty key) → Settings page (lookup select present) → Demo page (button works).
- **Result:** ✅ Generate button enabled in demo mode; demo banner shown; plan markdown rendered; Settings renders `Issue lookup by`; Demo page works. 
- **Error (test-side, fixed):** AppTest stale sidebar-radio references after widget updates → re-fetch after each `run()`; UTF-8 console printing needed for emoji labels. No app-code defects found.
- **Next:** By-title lookup mock test.

### 18:00 — By-title lookup mock test
- **Action:** Mocked the Jira `/search` endpoint to verify `fetch_issue_by_title()` builds the right JQL.
- **Result:** ✅ Returns normalized issue; requests `/rest/api/3/search` with `summary ~ "password reset" ORDER BY updated DESC`.
- **Error:** None.
- **Next:** Run the app live to confirm.

### 18:02 — Live run
- **Action:** `streamlit run app.py --server.headless true --server.port 8501`.
- **Result:** ✅ Health `ok`; root HTTP 200. Demo-mode Generate flow works end-to-end in the real UI.
- **Error:** None.
- **Next:** User adds real Jira + Groq credentials → live ticket generation. (Phase 5 Trigger remains after that.)

---

## Session 4 — Live credential verification (Chapter_03 .env)

### 18:10 — Sourced credentials from Chapter_03
- **Action:** Read `Chapter_03_Local_LLMs/Assignment_02_Local_Test_Case_Generator/Assets/src/.env` + `config.json`.
- **Result:** Found Jira creds (`simransatpathy96.atlassian.net`) + a Groq key. Seeded them into `Test-Plan-Agent-Blast/.env` (git-ignored) with a note that Jira looked stale.
- **Error:** None.
- **Next:** Probe both APIs live.

### 18:12 — Live API probes
- **Action:** Hit Jira `/myself` (v3+v2) and Groq `/models` + a chat.
- **Result:** ✅ **Groq works** — key valid, **`openai/gpt-oss-120b` available**, chat returns 200. ❌ **Jira 401** on both versions (token expired/revoked); `JIRA-101` → 404. Jira needs a fresh token from the user.
- **Error:** Jira token dead (recorded in findings §9).
- **Next:** Run the live Groq-enriched pipeline.

### 18:15 — First live Groq pipeline run → HTTP 400
- **Action:** Full pipeline (fixture → skeleton → Groq chat with `response_format=json_object`).
- **Result:** Groq connection + model OK, but chat returned **400 `json_validate_failed`** on the large prompt.
- **Error (fixed):** strict JSON mode rejects very large prompts → added **automatic retry without `response_format`** in `chat_json`; parse failures of non-objects also retry. SOP-02 updated first (Golden Rule).
- **Next:** Rerun.

### 18:20 — Second live run → model echoed input
- **Action:** Reran; the fallback worked (no 400) but the model returned `{'issue','skeleton'}` — it **echoed the input** instead of refined prose.
- **Error (fixed):** prompt lacked an explicit output contract → added an **exact output JSON schema** to `GROQ_SYSTEM_PROMPT` + a compact `GROQ_OUTPUT_SHAPE` reminder appended to the user prompt.
- **Next:** Rerun.

### 18:25 — Live enrichment VERIFIED ✅
- **Action:** Clean verification run with a deep-copied pristine baseline.
- **Result:** Final plan genuinely enriched vs the deterministic skeleton:
  - Summary rewritten professionally.
  - Scenario `S-01`: "Verify: User can request a reset link…" → **"Request password reset link with a valid registered email"**.
  - TC-01 steps became concrete: *"Navigate to the login page and click 'Forgot password' → enter email → submit → verify confirmation + email sent"*.
  - Risks + exit criteria refined and realistic.
  - Validation clean; enriched markdown saved to `output/TestPlan_DEMO-101_enriched.md`.
- **Error:** None.
- **Next:** Update docs; await a fresh Jira token from the user for the final live-ticket run.

### 18:30 — Render fix: double-numbered steps
- **Action:** Reviewed the enriched markdown; the LLM returned steps already prefixed with numbers, and the renderer added its own → output showed "1. 1. Navigate…".
- **Error (fixed):** added `_strip_step_number()` in `plan_engine.to_markdown` (handles "N." / "N)" / "N -"), re-rendered `output/TestPlan_DEMO-101_enriched.md` cleanly. SOP-03 updated first (Golden Rule).
- **Result:** Steps now render as a single clean numbered list.
- **Next:** Final docs sync + user provides a fresh Jira token.

---

## Session 5 — STLC framework integration (Chapter_02 STLC_SKILLS)

### 19:05 — Researched the STLC skills
- **Action:** Read the `Chapter_02/Prompt Templates/STLC_SKILLS` skill set — `test-plan-generator` (SKILL.md, `requirement-checklist.md`, `test-plan-template.md`, `fetch_jira.sh`), `jira-requirement-analyzer`, `test-scenario-designer`, plus the RICE-POT testcase templates.
- **Result:** Identified the valuable deltas for our Test Plan Creator: gap-analysis checklist, P0/P1/P2 risk model, scenario type tagging, and the HUMAN REVIEW GATE (DRAFT status).
- **Error:** None.
- **Next:** SOP/constitution updates (docs before code).

### 19:10 — Golden Rule: docs first
- **Action:** Updated `architecture/SOP-03-plan-engine.md` (STLC output model, schema 2.0.0, DRAFT + review gate) and `LLM.md` §2.3 (full v2 schema with `gap_analysis`, `type`/`priority`/`maps_to`, `review_gate`).
- **Result:** Constitution reflects the intended shape before code changed.
- **Error:** None (removed a leftover duplicate JSON tail fragment from LLM.md).
- **Next:** Code.

### 19:15 — Code: plan_engine v2
- **Action:** Added to `tools/plan_engine.py`:
  - `status: "DRAFT"` + `review_gate` block on every plan;
  - `_build_gap_analysis()` — deterministic STLC gap checklist (ACs, negative/boundary, perf/security, data/env, wording clarity);
  - scenario `type` (positive/negative/boundary/regression) + `maps_to` (AC-n/summary/gap);
  - P0/P1/P2 priorities (AC-verifying → P0);
  - validate() extended (checks status/gap_analysis/review_gate, priority ∈ P0-P2, type vocabulary);
  - renderer: DRAFT banner, "2. Gaps & Questions", scenario summary table, "⛔ HUMAN REVIEW GATE" tail;
  - schema_version bumped to `2.0.0`.
- **Result:** Offline skeleton test passed (6 scenarios P0/P1/P2, 4 gap entries, clean validation, all STLC markers in markdown).
- **Error:** None.
- **Next:** Live Groq prompt update.

### 19:20 — Code: Groq prompt v2
- **Action:** Rewrote `GROQ_SYSTEM_PROMPT` + `GROQ_OUTPUT_SHAPE` in `tools/orchestrator.py` so the model returns the STLC shape (`gap_analysis`, `review_gate`, scenario `type`/`priority`/`maps_to`); `merge_groq_content` extended to merge gaps/gate/type/priority.
- **Result:** Live Groq run returned all 7 keys; 6 scenarios typed/tagged; validation clean; schema 2.0.0.
- **Error:** None.
- **Next:** Verify the rendered document.

### 19:28 — Live STLC document verified ✅
- **Action:** Reviewed `output/TestPlan_DEMO-101_STLC.md`.
- **Result:** Professional STLC output — DRAFT banner, 4-row Gaps & Questions table, scenario summary table (S-01..S-06 with P0/P1/P2 + type + maps_to), concrete enriched steps, traceability, exit criteria referencing P0, and a closing HUMAN REVIEW GATE with the 4 open questions.
- **Error:** None.
- **Next:** UI verification.

### 19:33 — UI verification
- **Action:** AppTest across Generate (demo) / Settings / Demo pages + a live `streamlit run` on port 8502.
- **Result:** ✅ All pages render with the v2 schema; demo plan markdown contains the DRAFT banner + HUMAN REVIEW GATE; health `ok`, root HTTP 200. Server stopped after.
- **Error:** First background launch on 8501 was interrupted (exit 0xC000013A) — restarted on 8502 successfully.
- **Next:** Docs sync (this entry).

---

## Template for future entries (copy & fill)

```
### HH:MM — <short title>
- **Action:** <what was attempted>
- **Result:** <what happened / what was produced>
- **Error:** <error message + root cause if any>
- **Next:** <immediate next step>
```

---

## ⚠️ Known Issues / Blockers

| # | Blocker | Status |
|---|---------|--------|
| B1 | Real Jira credentials not yet entered in Settings — the Chapter_03 token is expired (401). **User must generate a fresh Jira API token** | 🔴 Awaiting user |
| B2 | ~~Groq key missing~~ | ✅ Resolved Session 4 — key sourced from Chapter_03, verified live |
| B3 | Live end-to-end run against a real Jira ticket | 🟡 Blocked by B1 |
| B4 | Phase 5 (Trigger automation: webhook/CLI scheduling) | 🟡 Pending by design |
| B5 | ~~ADF renderer recursion~~ | ✅ Fixed (Session 2) |
| B6 | ~~`_AC_HEADING_PATTERNS` tuple used with `re.search`~~ | ✅ Fixed (Session 2) |
