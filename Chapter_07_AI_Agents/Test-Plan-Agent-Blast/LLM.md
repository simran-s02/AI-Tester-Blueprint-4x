# 🧠 LLM.md — Project Constitution (Data Schemas, Behavioral Rules, Architectural Invariants)

> Per B.L.A.S.T. Protocol 0, this file is the **Project Constitution**. It is the single source of truth for *how the system is shaped*. If you change the logic, update the SOP in `architecture/` first — then update this file only if the shape of the world changed.

**Project:** Test Plan Creator from a Jira ID
**Last Updated:** 2026-09-05 16:50 (Phase 1–4 complete)
**Status:** APPROVED (Discovery answered; blueprint approved; Phases 1–4 done)

---

## 1. Thinking / Design Philosophy

My core assumption while designing this:

- **LLMs are probabilistic; business logic must be deterministic.** The LLM's job is *generation of test scenarios and prose* — but the pipeline (fetch → parse → structure → deliver) must be plain, testable code.
- **Data-First:** The JSON "payload" shapes are the contract. Everything (scripts, SOPs, LLM prompts) is built against the schema, never against a specific ticket.
- **Never guess business logic.** Field locations (acceptance criteria!), auth method, and Jira version are *discovered* or *user-provided in Settings*. Each "unknown" is surfaced in the UI, never silently assumed.
- **Single input, rich output:** a Jira issue key in → a structured Test Plan out, where every test case traces back to an acceptance criterion or requirement segment.
- **UI-first, thin orchestration:** Streamlit is the Navigation layer — it calls the `tools/` pipeline in-process. No subprocess scripts; modules are importable and testable.

---

## 2. JSON Data Schemas (APPROVED)

> `{ }` = object, `[ ]` = array, `?` = optional. Field names are snake_case for the internal contract.

### 2.1 Settings Schema (`.app_settings.json`)

```json
{
  "jira": {
    "base_url": "https://your-domain.atlassian.net",
    "email": "you@example.com",
    "api_token": ""
  },
  "groq": {
    "api_key": "",
    "model": "openai/gpt-oss-120b"
  }
}
```

### 2.2 Normalized Jira Issue Schema (`issue.normalized`)

```json
{
  "key": "PROJ-123",
  "id": "10001",
  "type": "Story",
  "status": "In Progress",
  "priority": "High",
  "summary": "As a user, I can reset my password",
  "description_md": "Markdown-converted description...",
  "acceptance_criteria": ["User can request a reset link", "Link expires in 30 min"],
  "components": ["Backend"],
  "labels": ["auth", "p1"],
  "linked_issues": [
    {
      "key": "PROJ-124",
      "type": "Sub-task",
      "summary": "...",
      "status": "Done",
      "link_type": "Relates"
    }
  ]
}
```

### 2.3 Test Plan Schema (`test_plan`) — the output contract (v2, STLC-aligned)

> v2 incorporates the STLC framework from `Chapter_02/Prompt Templates/STLC_SKILLS`
> (`test-plan-generator` + `jira-requirement-analyzer`): P0/P1/P2 risk tags, scenario
> types, a gap-analysis section, and the HUMAN REVIEW GATE (plans are DRAFT drafts).

```json
{
  "meta": {
    "jira_id": "PROJ-123",
    "generated_at": "2026-09-05T16:50:00+08:00",
    "engine": "BLAST-test-plan-creator",
    "schema_version": "2.0.0",
    "model": "openai/gpt-oss-120b"
  },
  "status": "DRAFT",
  "summary": "One-paragraph test objective derived from the ticket.",
  "scope": {
    "in_scope": ["Password reset flow", "Email delivery"],
    "out_of_scope": ["Third-party email provider internals"]
  },
  "gap_analysis": [
    {
      "area": "Functional / Negative paths",
      "finding": "No error path described for an invalid/expired reset link",
      "severity": "⚠️ ambiguous",
      "question": "What should the user see when the link has expired?"
    }
  ],
  "coverage_requirements": [
    {
      "requirement": "User can request a reset link",
      "source": "acceptance_criteria[0]",
      "test_cases": ["TC-01", "TC-02"]
    }
  ],
  "test_scenarios": [
    {
      "id": "S-01",
      "name": "Happy path - request reset link",
      "type": "positive",
      "priority": "P0",
      "maps_to": "AC-1",
      "preconditions": ["Authenticated user exists"],
      "test_cases": [
        {
          "id": "TC-01",
          "title": "Verify reset email is sent on valid request",
          "steps": ["Open /forgot-password", "Enter email", "Submit"],
          "expected": "Reset link email arrives within 30s",
          "data": { "email": "valid@example.com" }
        }
      ]
    }
  ],
  "risks": ["Email delivery latency", "Rate limiting on resend"],
  "exit_criteria": "All P0/P1 cases pass; no open Severity-1 defects.",
  "review_gate": {
    "assumptions": ["Email provider latency assumed out of scope"],
    "open_questions": ["Are 30-minute link expiries acceptable to product?"]
  },
  "generation": {
    "mode": "groq",
    "error": null
  }
}
```

---

## 3. Behavioral Rules (Constitution — immutable unless user overrides)

1. **Deterministic skeleton first.** The generator produces scenario IDs (S-01, TC-01…) by fixed rules from the parsed schema — the LLM only fills in human-readable prose inside that skeleton.
2. **Every test case must trace to a source** (acceptance criterion, requirement segment, or explicit user rule). No orphan cases. If no source exists → flag as a gap, don't invent one.
3. **Don't guess unknowns — surface them.** Unknown field mapping → user provides via Settings; never a hardcoded guess.
4. **No secrets in code.** `.env` / `.app_settings.json` only; scripts read settings; both are git-ignored.
5. **Idempotent by design.** Re-running the same Jira ID yields the same structure; `generated_at` is the only volatile field.
6. **Normalize before analyze.** ADF/wiki markup → markdown → plain semantics. Never regex-parse raw ADF.
7. **Scope guard:** operate only inside `Chapter_07_AI_Agents/Test-Plan-Agent-Blast/`. `.tmp/` for intermediates.
8. **LLM output is a draft.** A deterministic validator checks the LLM-generated plan against the schema (required keys, traceability, ID format) before delivery.
9. **Resilient LLM:** if Groq is unreachable/misconfigured, the pipeline still returns a complete **deterministic fallback plan** (clearly flagged), so the Link can never silently produce an empty test plan.
10. **Connection test before full run:** Settings exposes Test Connection for Jira + Groq; Generate page validates the Link and stops with a clear error if broken.

---

## 4. Architectural Invariants (B.L.A.S.T. / A.N.T.)

**Layer 1 — Architecture (`architecture/`):** Markdown SOPs. Each SOP defines: goal, input schema, tool logic, edge cases. **Golden Rule:** logic changes → update SOP *before* code.

**Layer 2 — Navigation (UI + orchestrator):** Streamlit `app.py` (Settings + Generate pages) routes data between SOPs and tools via `tools/orchestrator.py`. Holds no business logic itself.

**Layer 3 — Tools (`tools/`):** Deterministic Python modules, atomic + testable:

```
tools/
  config_store.py    # settings: load/save .app_settings.json + .env merge + validation
  jira_client.py     # test_connection(); fetch_issue(); normalize (ADF/wiki/plain -> md); extract ACs
  groq_client.py     # test_connection() -> list models; chat() -> JSON content with fallback
  plan_engine.py     # deterministic skeleton + coverage + validate + markdown render
  orchestrator.py    # thin nav: jira_id + settings -> test_plan dict; CLI entry
  fixtures/sample_issue.json   # offline demo payload
```

**Data flow (read-only after each step):**

```
User prompt ("Fetch PROJ-123 ...") 
  → Settings (.app_settings.json)
  → tools/orchestrator.py
      → tools/jira_client.fetch_issue()     → issue.normalized
      → tools/plan_engine.build_skeleton()  → skeleton (deterministic)
      → tools/groq_client.chat()            → prose content (JSON mode)
      → tools/plan_engine.validate()        → test_plan dict
  → app.py renders stylized .md + offers download
```

**Edge cases the SOPs must cover:**
- Ticket has no acceptance criteria → gap report surfaced in the plan.
- Description is ADF vs wiki markup vs plain text → auto-normalize all three.
- Custom field IDs differ between instances → auto-scan custom fields for "acceptance" match.
- Jira rate limits → single issue fetch + batch linked-key JQL search.
- Issue key not found / no permission → distinct error codes, no silent empty plan.
- Groq model name/availability drift → Settings lists live models from the models endpoint.

---

## 5. What I Think About Schemas, Rules & Architecture (Open Commentary)

- **On schemas:** the settings/normalized-issue/test-plan split is the most important decision. If I let raw Jira JSON leak into the generator, every instance difference breaks the logic. The **normalized schema is the contract** — fetch and map once, downstream never cares about Jira specifics.
- **On rules:** rule 2 (traceability) is what makes the output *trustworthy*. A test plan that can't point back to the requirement is decoration. Rule 8 (LLM output is a draft) plus rule 9 (deterministic fallback) keep the probabilistic part safe.
- **On architecture:** the 3-layer split means the LLM never touches Jira directly and never formats delivery — it only writes prose inside a pre-validated skeleton. That keeps us deterministic and testable, and the Navigation layer thin.
- **On Groq:** OpenAI-compatible API means the tool layer stays provider-agnostic. We request `response_format=json_object` and conservative params so `openai/gpt-oss-120b` (and any fallback model) work without hard model-specific coupling.
- **Future (Trigger phase):** once reliable, this pipeline can be triggered by a webhook on Jira status → "In QA", or a CLI (`python -m tools.orchestrator PROJ-123`). Input schema is already isolated so this is additive, not a rewrite.

---

## 6. Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-09-05 | Draft created (Protocol 0) | System Pilot |
| 2026-09-05 | APPROVED: Discovery answered (Jira+Groq, UI, Settings); added rule 9/10, Settings schema, `generation` field, Groq notes | System Pilot |
| 2026-09-05 | Phases 1–4 implemented + verified (fixture smoke test, edge tests, AppTest, local run). Tooling revised to importable `tools/` modules. | System Pilot |
| 2026-09-05 | Session 3: `demo_mode` fallback (Generate works without creds), `issue_lookup_by` setting (key vs title JQL), `fetch_issue_by_title()`, SOP-04 updated first. | System Pilot |
| 2026-09-05 | Session 4: **Groq verified live** (`openai/gpt-oss-120b`); Jira token from Chapter_03 expired (401). Added strict-JSON-mode retry fallback + explicit output schema in the LLM prompt. | System Pilot |
| 2026-09-05 | Session 5: **STLC integration** (schema 2.0.0) — gap analysis, P0/P1/P2 priorities, scenario types + maps_to, DRAFT status + HUMAN REVIEW GATE. From Chapter_02 STLC_SKILLS. | System Pilot |
