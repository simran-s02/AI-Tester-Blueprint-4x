# SOP-03 — Test Plan Engine (Deterministic Skeleton + Validate + Render)

**Layer:** 3 (Tools) · **Module:** `tools/plan_engine.py` · **Status:** Implemented

## Goal
Turn a **normalized Jira issue** into a complete test plan dict. The skeleton, traceability, IDs, and validation are **deterministic**; only human-readable prose is delegated to the LLM (and even that has a deterministic fallback).

## Output model (STLC-aligned — from Chapter_02 STLC_SKILLS/test-plan-generator)
The plan follows the industry STLC "review-ready draft" shape:
1. Scope & Objectives (in/out of scope + objective)
2. **Gaps & Questions for the author** (gap analysis table)
3. Test Scenarios — each tagged **P0/P1/P2** risk + **type** (positive/negative/boundary/regression) + maps to an AC or a gap
4. Test Data & Environment
5. Risks & Assumptions
6. Entry / Exit criteria
- **HUMAN REVIEW GATE** — the plan is always a DRAFT pending human approval; a missing
  acceptance criterion is a finding, never a blank to fill.
- Schema version bumped to `2.0.0`; a new `status: "DRAFT"` + `review_gate` block carry the gate.

## Input
- `issue` (normalized dict, schema §2.2)
- `settings` (for `model`, engine metadata)
- `groq_content` (optional dict from the LLM)

## Behavior

### Step 1 — `build_skeleton(issue, settings)`
- `summary`: one paragraph stating objective derived from summary + type + priority.
- `scope`: in_scope = [summary, each linked issue summary]; out_of_scope = [] unless description implies exclusion.
- `coverage_requirements`: map each acceptance criterion to a stable id `AC-01…`.
- `test_scenarios`: deterministic starter scenarios derived from criteria + issue type:
  - each criterion → a scenario (`S-0n` "Verify <criterion>");
  - plus issue-type defaults (Story/Bug/Epic) such as happy path / negative / boundary.
- Every scenario gets 1–2 deterministic test cases `TC-…` with steps derived from the criterion, expected result referencing the criterion.
- `risks`: derived from issue (high priority → risk; bug → regression risk; etc.).
- `exit_criteria`: standard QA exit criteria string.

### Step 2 — `merge_groq_content(skeleton, groq_content, issue)`
The LLM may refine **prose** fields only: `summary`, `scope`, scenario `name`/`steps`/`expected` wording, `risks`, `exit_criteria`. It may **not** change ids, traceability, or structure. Merge field-by-field with the skeleton as the source of truth; ignore unknown keys.

### Step 3 — `validate(plan)`
Check required keys exist (`meta`, `summary`, `coverage_requirements`, `test_scenarios`), each scenario has an id matching `S-\d+`, each case has `TC-…`, and every `coverage_requirements[].test_cases` reference real case ids. Collect errors; if any are structural, return them so orchestrator can surface.

### Step 4 — `to_markdown(plan)`
Render a professional Test Plan document with tables and a traceability matrix.
- Steps are re-numbered by the renderer; any leading "N." / "N)" / "N -" the LLM added
  to a step string is stripped first (`_strip_step_number`) so we never get "1. 1. Do x".

## Edge Cases
- Zero acceptance criteria → still produce scenarios from summary/type; add gap note in risks.
- LLM returns nothing/error → `validate` on the pure skeleton passes (it is already complete).
- Duplicate/empty criteria → dedupe; skip empties.

## Golden Rule
If plan logic changes, update this SOP first, then the code.
