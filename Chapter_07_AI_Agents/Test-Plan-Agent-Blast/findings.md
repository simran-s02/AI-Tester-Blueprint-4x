# 🔎 Findings — Research, Discoveries & Constraints

**Project:** Test Plan Creator from a Jira ID
**Protocol:** 0 — Initialization (B.L.A.S.T.)
**Last Updated:** 2026-09-05 16:50 (Phase 1–4 complete)

---

## 1. What We Learned About the Problem

- The input is a **single Jira issue key** (e.g. `PROJ-123`).
- The desired output is a **complete Test Plan**: derived from the ticket's description, acceptance criteria, and linked issues (sub-tasks, bugs, stories).
- The main challenge is **structured extraction from unstructured Jira text** (ADF / wiki markup) and turning it into a deterministic plan skeleton that the LLM then fleshes out.
- Business logic (what "good coverage" means) must be **rules-based and deterministic**; the LLM should only generate prose/scenarios within that guardrail.
- Source of truth for requirements = **Jira Cloud REST API v3** (or v2 for Server/DC — must be confirmed during Discovery).

---

## 2. Jira API Findings (Source of Truth)

### Auth Options (to confirm during Discovery)

| Method | Best for | Notes |
|--------|----------|-------|
| **PAT (Personal Access Token)** | Cloud | `Authorization: Bearer <token>`, cleanest |
| API Token + email (Basic) | Cloud | Base64 of `email:api_token` |
| Username + password (Basic) | Server/DC | Legacy |
| OAuth 2.0 (3LO) | Cloud apps | Not needed for a local tool |

### Key Endpoints (Cloud — REST API v3)

| Purpose | Endpoint | Notes |
|---------|----------|-------|
| Handshake / verify creds | `GET /rest/api/3/myself` | Returns the current user |
| Get issue | `GET /rest/api/3/issue/{issueIdOrKey}` | Core call for our tool |
| Search (JQL fallback) | `GET /rest/api/3/search` | `?jql=...` when we need issue lists |
| Get issue links | Included in `GET issue` via `fields.issuelinks` | No separate endpoint needed for links |
| Get transitions | `GET /rest/api/3/issue/{key}/transitions` | For Trigger phase (status-based automation) |

### Important Field IDs (useful but names differ per project)

- `summary`, `description`, `issuetype`, `priority`, `status`, `components`, `labels`, `fixVersions`
- `acceptance criteria` is **often NOT a default field** — it may be:
  - Custom field (e.g. `customfield_10020`) → must discover per-instance
  - Written inside the **description** under an "Acceptance Criteria" heading → must parse
  - A separate linked issue type → must fetch links
- `issuelinks` gives linked issues (blocks / is blocked by / relates to / cloned from) → useful to pull sub-tasks & related bugs into the plan.
- Jira Cloud descriptions are **ADF (Atlassian Document Format)** JSON; Server often uses **wiki markup**. Both need conversion to plain text/markdown before analysis.

---

## 3. Requests / Curl Examples We Will Use

> Credentials assumed in `.env` as `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` or `JIRA_PAT`.
> Windows note: use `curl.exe` (real curl) — PowerShell aliases `curl` to `Invoke-WebRequest`.

### 3.1 Handshake (Phase 2 — Link verification)

```bash
# PAT auth (Cloud)
curl.exe -s -u "%JIRA_EMAIL%:%JIRA_API_TOKEN%" ^
  -H "Accept: application/json" ^
  "%JIRA_BASE_URL%/rest/api/3/myself"

# Bearer token auth
curl.exe -s -H "Authorization: Bearer %JIRA_PAT%" ^
  -H "Accept: application/json" ^
  "%JIRA_BASE_URL%/rest/api/3/myself"
```

### 3.2 Fetch a single issue by ID/Key (core call)

```bash
# Minimal fields we need for the test plan
curl.exe -s -u "%JIRA_EMAIL%:%JIRA_API_TOKEN%" ^
  -H "Accept: application/json" ^
  "%JIRA_BASE_URL%/rest/api/3/issue/PROJ-123?fields=summary,description,issuetype,priority,status,labels,components,issuelinks,customfield_10020"
```

> Without `?fields=` Jira returns ~all fields (huge payload). Always request only what we need.

### 3.3 Get linked issues (sub-tasks, related bugs)

```bash
# First: read `fields.issuelinks` from the issue response, collect the linked keys,
# then fetch each one (or use JQL search to grab them in one call):
curl.exe -s -u "%JIRA_EMAIL%:%JIRA_API_TOKEN%" ^
  -H "Accept: application/json" ^
  -G "%JIRA_BASE_URL%/rest/api/3/search" ^
  --data-urlencode "jql=key in (PROJ-124, PROJ-125, PROJ-126) AND issuetype in (Sub-task, Bug)" ^
  --data-urlencode "fields=summary,status,issuetype,priority"
```

### 3.4 Unix-style curl (for Git Bash / WSL / Linux)

```bash
# Core issue fetch (PAT)
curl -s -H "Authorization: Bearer $JIRA_PAT" \
  -H "Accept: application/json" \
  "$JIRA_BASE_URL/rest/api/3/issue/PROJ-123?fields=summary,description,issuetype,priority,status,issuelinks"
```

### 3.5 What we expect back (shape snapshot)

```json
{
  "id": "10001",
  "key": "PROJ-123",
  "fields": {
    "summary": "As a user, I can reset my password",
    "description": { "type": "doc", "content": [ ] },
    "issuetype": { "name": "Story" },
    "priority": { "name": "High" },
    "status": { "name": "In Progress" },
    "labels": ["p1", "auth"],
    "components": [{ "name": "Backend" }],
    "issuelinks": [
      { "type": { "name": "Relates" },
        "outwardIssue": { "key": "PROJ-124", "fields": { "summary": "..." } } }
    ]
  }
}
```

---

## 4. Discoveries & Constraints

- ✅ Jira Cloud REST **v3** is the modern default; **v2** if instance is Server/DC (Discovery question).
- ✅ **PAT or API token** is the simplest auth for a local deterministic tool.
- ⚠️ **Acceptance Criteria location varies per instance** → must be discovered, not assumed.
- ⚠️ **Description format varies** (ADF JSON vs wiki markup) → normalize before parsing.
- ⚠️ Custom fields (`customfield_*`) differ per Jira project → need a **field-mapping config**.
- ⚠️ Rate limits exist on Cloud (per-user ~10 req/s) → use batching (JQL `key in (...)`) instead of N sequential calls.
- 🚫 No GitHub/library research executed **yet** — that belongs to Phase 1 step 3 (Research) and is currently halted by Protocol 0.
- 🚫 No `tools/` scripts written — blocked until blueprint approval (Protocol 0 HALT).
- ✅ **Lifted 16:45** — user approved full scope; tools/ built in Session 2.

---

## 5. Open Questions (RESOLVED — Discovery complete)

| # | Question | Answer |
|---|----------|--------|
| 1 | Jira version? | Cloud v3 default, v2 fallback (auto-detect) |
| 2 | Credentials? | API token + email; stored via Settings UI / `.env` |
| 3 | Acceptance criteria location? | Auto-detect (custom field → ADF → description headings) |
| 4 | Input scope? | Story + linked sub-tasks/bugs (user picks) |
| 5 | Output? | Rendered Test Plan in UI + downloadable `.md` |
| 6 | Trigger? | Manual prompt in UI ("Fetch this Jira and create a test plan"); Trigger phase later |

---

## 6. GROQ API Findings (added Phase 1 research)

- Provider: **Groq** (`https://api.groq.com`) — OpenAI-compatible REST endpoints.
- LLM: user specified an **open 120B-parameter GPT model** → Groq hosts **`openai/gpt-oss-120b`**. Open-weight model name pattern on Groq: `openai/gpt-oss-120b`. (Exact availability/moniker should be verified via `GET /openai/v1/models` in Settings → Test Connection, and listed in the dropdown.)
- Fallbacks (also open-weight, Groq-hosted): `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`.
- Groq chat endpoint: `POST https://api.groq.com/openai/v1/chat/completions`
- Groq models endpoint: `GET https://api.groq.com/openai/v1/models`
- Auth: `Authorization: Bearer gsk_...`
- Groq supports **JSON mode** (`response_format={"type":"json_object"}`) and **reasoning models** (e.g. `openai/gpt-oss-120b` supports `reasoning_effort`); not all params apply to all models → we send params conservatively.

---

## 7. Tooling Decision (revised from original plan)

- Original plan proposed separate `fetch_jira.py` / `normalize_issue.py` / etc. scripts.
- **Revised:** because the UI (Navigation layer) calls the pipeline in-process, we use importable modules under `tools/` instead of subprocess scripts:
  - `config_store.py` — read/write `.app_settings.json` + `.env` merge
  - `jira_client.py` — connection test + fetch/normalize issue (ADF/wiki/plain)
  - `groq_client.py` — connection test (list models) + chat completion (JSON mode)
  - `plan_engine.py` — deterministic skeleton + `generate_content` + validate
  - `orchestrator.py` — thin Navigation: issue key → test plan dict; also exposes CLI `python -m tools.orchestrator`
  - `fixtures/sample_issue.json` — offline demo payload (no credentials required)

---

## 8. Research Targets (completed Phase 1 step 3)

- ✅ `streamlit` for the simple UI (Python, minimal setup)
- ✅ `requests` for REST calls (no heavy SDK dependency)
- ✅ `python-dotenv` for `.env`
- ✅ Groq OpenAI-compatible API shape (chat completions + models)
- ✅ Jira ADF (Atlassian Document Format) → markdown extraction strategy
- ✅ Jira Cloud v3 (`/rest/api/3`) vs Server v2 (`/rest/api/2`) endpoint detection

---

## 9. Live Verification Results (Session 4 — 2026-09-05)

### GROQ — ✅ VERIFIED LIVE
- Working key sourced from `Chapter_03_Local_LLMs` assignment `.env`.
- `GET /openai/v1/models` → **200**, 14 models available.
- **`openai/gpt-oss-120b` is available** on the account and chat-completes successfully.
- Full pipeline (fixture issue → skeleton → **live Groq enrichment** → merge → validate) passed.
- Enrichment is genuine: final plan has concrete steps ("Navigate to the login page and click 'Forgot password'…"), realistic risks, and crisp exit criteria vs the generic deterministic skeleton.
- Output: `output/TestPlan_DEMO-101_enriched.md`.

### JIRA — ❌ NOT VERIFIED (credentials expired)
- Chapter_03 Jira token (`simransatpathy96.atlassian.net`) → **401** on both `/rest/api/3` and `/rest/api/2`.
- `JIRA-101` → **404** (does not exist or no permission).
- Action needed: **user must provide a valid Jira API token** in Settings.

### Robustness fixes made from live findings
- `groq_client.chat_json` now **retries without `response_format`** when strict JSON mode fails
  (HTTP 400 `json_validate_failed`, or a non-object parse) — large prompts can trip strict mode.
- Orchestrator prompt now includes an **explicit output JSON schema** + a compact shape reminder,
  so the model returns mergeable prose instead of echoing the input skeleton.

---

## 10. STLC Framework Integration (Session 5 — from Chapter_02 STLC_SKILLS)

**Source:** `Chapter_02_Prompt_Engineering/Prompt Templates/STLC_SKILLS/`
(`test-plan-generator`, `jira-requirement-analyzer`, `test-scenario-designer`).

### What was adopted (test-plan output model v2, schema `2.0.0`)
- **Gap analysis** — `gap_analysis[]` rows: area / finding / severity (✅ present · ⚠️ ambiguous · ❌ missing) / question to author.
  Deterministic version (`_build_gap_analysis`) checks: ACs testable?, negative/error/boundary described?, summary present?,
  non-functional (perf/security/roles), data & environment, ambiguous wording. Every gap becomes an open question.
- **P0/P1/P2 risk model** replaces High/Medium. AC-verifying scenarios → P0; happy path → P1; negative → P1; boundary → P2; regression → P0.
- **Scenario type tagging** — `type`: positive / negative / boundary / regression; `maps_to`: AC-n / summary / gap.
- **HUMAN REVIEW GATE** — plan carries `status: "DRAFT"` and a `review_gate` block (assumptions + open questions);
  markdown ends with a review gate + "Approve or edit before test cases are written".
- **Renderer** — sections renumbered to the STLC template: 1 Scope & Objectives, 2 Gaps & Questions,
  3 Test Scenarios (summary table + per-scenario detail), 4 Requirements Traceability, 5 Risks, 6 Entry/Exit, then the gate.

### Not adopted (out of scope for this tool)
- The skills' *mandatory stop-for-human-approval loop* (our tool generates a DRAFT and the human owns sign-off in the UI).
- `test-case-writer` / `test-data-generator` / defect-management / execution phases — the tool covers Test Planning only.
