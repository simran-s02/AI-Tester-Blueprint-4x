"""Deterministic test-plan engine: skeleton, LLM merge, validate, render.

The skeleton, ids, traceability, and validation are pure functions of the
normalized issue. The LLM may only refine prose inside that skeleton.
See architecture/SOP-03-plan-engine.md and LLM.md section 2.3.
"""

from __future__ import annotations

import datetime as _dt
import re
from typing import Any, Optional

SCHEMA_VERSION = "2.0.0"
ENGINE = "BLAST-test-plan-creator"


# ---------------------------------------------------------------- skeleton
def build_skeleton(issue: dict, model: str = "", mode: str = "groq") -> dict:
    """Build a complete, deterministic test plan from a normalized issue."""
    key = issue.get("key", "UNKNOWN")
    summary = issue.get("summary", "") or ""
    issue_type = issue.get("type", "") or "Issue"
    priority = issue.get("priority", "") or "Medium"
    criteria = [c for c in (issue.get("acceptance_criteria") or []) if c]
    linked = issue.get("linked_issues") or []
    now = _dt.datetime.now(_dt.timezone.utc).astimezone().isoformat(timespec="seconds")

    # --- coverage requirements -------------------------------------
    coverage = []
    for idx, criterion in enumerate(criteria, start=1):
        coverage.append(
            {
                "requirement": criterion,
                "source": f"acceptance_criteria[{idx - 1}]",
                "test_cases": [],
            }
        )
    if not coverage:
        coverage.append(
            {
                "requirement": summary or f"{key} requirements",
                "source": "issue.summary",
                "test_cases": [],
            }
        )

    # --- scenarios + test cases -------------------------------------
    scenarios: list[dict] = []
    scenario_idx = 0
    case_idx = 0

    def _add_scenario(
        name: str,
        cases: list[dict],
        tag: str = "positive",
        maps_to: str = "",
    ) -> None:
        nonlocal scenario_idx, case_idx
        scenario_idx += 1
        sc = {
            "id": f"S-{scenario_idx:02d}",
            "name": name,
            "type": tag,
            "priority": "P0" if str(maps_to).startswith("AC-") else _scenario_priority(issue_type, tag),
            "maps_to": maps_to,
            "preconditions": ["Jira issue is in a testable state", f"Issue {key} is accessible"],
            "test_cases": [],
        }
        for case in cases:
            case_idx += 1
            tc_id = f"TC-{case_idx:02d}"
            sc["test_cases"].append(
                {
                    "id": tc_id,
                    "title": case["title"],
                    "steps": case.get("steps", []),
                    "expected": case.get("expected", ""),
                    "data": case.get("data", {}),
                }
            )
            # traceability: link this TC id to its requirement source
            source = case.get("source")
            if source is not None:
                coverage[source]["test_cases"].append(tc_id)
        scenarios.append(sc)

    # Each acceptance criterion gets a positive verification scenario.
    for idx, criterion in enumerate(criteria):
        if not criterion.strip():
            continue
        short = _shorten(criterion, 70)
        _add_scenario(
            name=f"Verify: {short}",
            tag="positive",
            maps_to=f"AC-{idx + 1}",
            cases=[
                {
                    "title": f"Verify acceptance criterion {idx + 1} is met",
                    "steps": [
                        "Set up the precondition described by the criterion",
                        f"Execute the flow described in: {short}",
                        "Observe the result against the expected behavior",
                    ],
                    "expected": criterion,
                    "data": {"criterion": criterion},
                    "source": idx,  # index into coverage[]
                }
            ],
        )

    # Issue-type default scenarios ensure broad coverage even with 0 criteria.
    defaults = _type_default_scenarios(issue_type, key)
    for scenario in defaults:
        cases = []
        for step in scenario["cases"]:
            cases.append({**step, "source": None})
        _add_scenario(
            name=scenario["name"],
            tag=scenario.get("tag", "positive"),
            maps_to=scenario.get("maps_to", "gap"),
            cases=cases,
        )

    if not scenarios:
        _add_scenario(
            name=f"Smoke test {key}",
            tag="positive",
            maps_to="summary",
            cases=[
                {
                    "title": f"Basic smoke test of {key}",
                    "steps": [f"Open the feature described in {summary or key}"],
                    "expected": "Feature behaves per the ticket summary",
                }
            ],
        )

    # --- scope / risks / exit ---------------------------------------
    in_scope = [summary or key] if summary else [key]
    for li in linked:
        if li.get("summary"):
            in_scope.append(f"{li.get('key')} — {li.get('summary')}")
    out_of_scope = []
    risks = _derive_risks(issue_type, priority, summary)
    gap_analysis = _build_gap_analysis(issue, criteria)

    exit_criteria = (
        "All P0 scenarios pass with no open Severity-1 defects; "
        "acceptance criteria verify successfully; gaps raised in section 2 "
        "are answered or explicitly accepted by the author."
    )

    plan = {
        "meta": {
            "jira_id": key,
            "generated_at": now,
            "engine": ENGINE,
            "schema_version": SCHEMA_VERSION,
            "model": model or "deterministic",
            "source": {"type": issue_type, "status": issue.get("status", ""), "priority": priority},
        },
        "status": "DRAFT",
        "summary": _build_summary(issue, coverage),
        "scope": {"in_scope": in_scope, "out_of_scope": out_of_scope},
        "gap_analysis": gap_analysis,
        "coverage_requirements": coverage,
        "test_scenarios": scenarios,
        "risks": risks,
        "exit_criteria": exit_criteria,
        "review_gate": {
            "assumptions": ["Ticket text is the single source of truth used for this draft."],
            "open_questions": [g["question"] for g in gap_analysis if g.get("question")],
        },
        "generation": {"mode": mode, "error": None},
    }
    return plan


def _build_gap_analysis(issue: dict, criteria: list[str]) -> list[dict]:
    """Deterministic STLC-style gap analysis (from requirement-checklist.md).

    Marks ✅ present / ⚠️ ambiguous / ❌ missing per area and turns every gap
    into a question for the ticket author.
    """
    summary = (issue.get("summary") or "").strip()
    description = (issue.get("description_md") or "").strip()
    issue_type = (issue.get("type") or "").lower()
    gaps: list[dict] = []

    def add(area: str, finding: str, severity: str, question: str) -> None:
        gaps.append(
            {
                "area": area,
                "finding": finding,
                "severity": severity,
                "question": question,
            }
        )

    # Functional
    if not criteria:
        add(
            "Functional",
            "No testable acceptance criteria found on the ticket.",
            "❌ missing",
            "Can the author provide explicit, observable acceptance criteria?",
        )
    elif any(len(c.strip()) < 12 for c in criteria):
        add(
            "Functional",
            "Some acceptance criteria look too vague to be observable pass/fail.",
            "⚠️ ambiguous",
            "Please tighten the short/vague acceptance criteria into testable statements.",
        )
    if not summary:
        add(
            "Functional",
            "No user story / summary present.",
            "❌ missing",
            "What is the goal of this ticket in one sentence?",
        )
    if "bug" not in issue_type and not _mentions(description, ("error", "invalid", "fail", "empty", "boundary", "limit")):
        add(
            "Functional",
            "No negative / error / boundary paths described.",
            "⚠️ ambiguous",
            "What should happen on invalid input, empty state, or failure responses?",
        )

    # Non-functional (very often missing)
    if not _mentions(description + summary, ("perf", "load", "response time", "second", "ms")):
        add(
            "Non-functional",
            "No performance / load expectation stated.",
            "⚠️ ambiguous",
            "Are there performance or response-time expectations for this ticket?",
        )
    if not _mentions(description + summary, ("secur", "auth", "role", "permission", "admin", "access")):
        add(
            "Non-functional",
            "No security / roles / permissions expectation stated.",
            "⚠️ ambiguous",
            "Which roles or permissions can and cannot perform this action?",
        )

    # Data & environment
    if not _mentions(description, ("test data", "fixture", "seed", "environment", "feature flag", "config")):
        add(
            "Data & environment",
            "No test data or environment / feature-flag named.",
            "⚠️ ambiguous",
            "What test data, environment, or feature flags are required to test this?",
        )

    # Clarity
    if _mentions(summary + " " + description, ("etc", "handle gracefully", "should work", "as appropriate")):
        add(
            "Clarity",
            "Ambiguous wording found ('etc.', 'handle gracefully', 'should work').",
            "⚠️ ambiguous",
            "Can the ambiguous phrasing be made specific and testable?",
        )

    if not gaps:
        gaps.append(
            {
                "area": "Overall",
                "finding": "No blocking gaps detected in the automatic review.",
                "severity": "✅ present",
                "question": "",
            }
        )
    return gaps


def _mentions(text: str, needles: tuple) -> bool:
    lowered = text.lower()
    return any(n in lowered for n in needles)


def _type_default_scenarios(issue_type: str, key: str) -> list[dict]:
    """Default coverage per issue type, STLC-style: positive/negative/boundary/regression."""
    lower = (issue_type or "").lower()
    scenarios = [
        {
            "name": "Happy path — expected workflow succeeds",
            "tag": "positive",
            "maps_to": "summary",
            "cases": [
                {
                    "title": f"{key} main workflow completes successfully",
                    "steps": [
                        "Navigate to the feature entry point",
                        "Perform the primary user action",
                        "Confirm the success state is shown",
                    ],
                    "expected": "Primary workflow completes without errors",
                }
            ],
        },
        {
            "name": "Negative path — invalid input is handled",
            "tag": "negative",
            "maps_to": "gap",
            "cases": [
                {
                    "title": f"{key} handles invalid or empty input",
                    "steps": [
                        "Enter invalid or empty input",
                        "Submit the action",
                        "Observe validation feedback",
                    ],
                    "expected": "Graceful validation message; no crash",
                }
            ],
        },
        {
            "name": "Boundary — empty, minimum, and maximum conditions",
            "tag": "boundary",
            "maps_to": "gap",
            "cases": [
                {
                    "title": f"{key} behaves correctly at boundary conditions",
                    "steps": [
                        "Exercise empty input state",
                        "Exercise minimum and maximum allowed values",
                        "Confirm no crash and correct messaging",
                    ],
                    "expected": "Boundary states handled without error",
                }
            ],
        },
    ]
    if "bug" in lower:
        scenarios.insert(
            0,
            {
                "name": "Regression — reported defect does not recur",
                "tag": "regression",
                "maps_to": "summary",
                "cases": [
                    {
                        "title": f"Reproduce steps from {key} and verify fix",
                        "steps": [
                            "Reproduce the originally reported steps",
                            "Confirm the defect no longer occurs",
                            "Run a quick check of adjacent flows",
                        ],
                        "expected": "Original defect is fixed; adjacent flows unaffected",
                    }
                ],
            },
        )
    return scenarios


def _scenario_priority(issue_type: str, tag: str) -> str:
    """STLC risk model: P0 (must test) / P1 (should test) / P2 (best effort)."""
    lower = (issue_type or "").lower()
    if tag == "regression":
        return "P0"
    if tag == "positive":
        return "P0" if ("bug" in lower or not lower) else "P1"
    if tag == "negative":
        return "P1"
    if tag == "boundary":
        return "P2"
    return "P1"


def _derive_risks(issue_type: str, priority: str, summary: str) -> list[str]:
    risks = []
    lower_type = (issue_type or "").lower()
    if "bug" in lower_type:
        risks.append("Defect may indicate a wider regression across the module.")
    if (priority or "").lower() in ("highest", "high", "critical", "blocker"):
        risks.append("High-priority ticket — schedule testing early in the cycle.")
    if not summary:
        risks.append("Ticket has no summary — clarify requirements before deep testing.")
    if not risks:
        risks.append("Standard risk: incomplete requirements or missing test data.")
    return risks


def _build_summary(issue: dict, coverage: list[dict]) -> str:
    key = issue.get("key", "UNKNOWN")
    summary = (issue.get("summary") or "").strip()
    issue_type = (issue.get("type") or "issue").lower()
    count = len(coverage)
    if summary:
        return (
            f"This test plan validates {key}: “{summary}”. "
            f"It covers {count} requirement{'s' if count != 1 else ''} "
            f"derived from the {issue_type} and its acceptance criteria."
        )
    return (
        f"This test plan validates {key} ({issue_type}). "
        f"It covers {count} requirement{'s' if count != 1 else ''} "
        f"derived from the ticket."
    )


def _shorten(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


# ---------------------------------------------------------------- merge
def merge_groq_content(skeleton: dict, groq_content: Optional[dict]) -> dict:
    """Merge LLM prose refinements into the skeleton.

    The LLM may only change prose fields (summary, scenario titles/steps/
    expected wording, risks, exit criteria, out-of-scope notes). Structure,
    ids, and traceability stay owned by the skeleton.
    """
    plan = skeleton
    if not groq_content or not isinstance(groq_content, dict):
        return plan

    # summary / risks / exit criteria
    if isinstance(groq_content.get("summary"), str) and groq_content["summary"].strip():
        plan["summary"] = groq_content["summary"].strip()
    if isinstance(groq_content.get("risks"), list):
        new_risks = [str(r) for r in groq_content["risks"] if str(r).strip()]
        if new_risks:
            plan["risks"] = new_risks[:5]
    if isinstance(groq_content.get("exit_criteria"), str) and groq_content["exit_criteria"].strip():
        plan["exit_criteria"] = groq_content["exit_criteria"].strip()

    # gap analysis refinements (the LLM may sharpen findings/questions, not invent requirements)
    llm_gaps = groq_content.get("gap_analysis")
    if isinstance(llm_gaps, list):
        skeleton_gaps = {g.get("area", "").lower(): g for g in plan["gap_analysis"]}
        for gap in llm_gaps:
            if not isinstance(gap, dict) or not gap.get("area"):
                continue
            existing = skeleton_gaps.get(gap["area"].lower())
            if existing:
                if isinstance(gap.get("question"), str) and gap["question"].strip():
                    existing["question"] = gap["question"].strip()
                if isinstance(gap.get("finding"), str) and gap["finding"].strip():
                    existing["finding"] = gap["finding"].strip()

    # review gate refinements
    gate = groq_content.get("review_gate")
    if isinstance(gate, dict):
        if isinstance(gate.get("assumptions"), list):
            new_assumptions = [str(a) for a in gate["assumptions"] if str(a).strip()]
            if new_assumptions:
                plan["review_gate"]["assumptions"] = new_assumptions[:5]
        if isinstance(gate.get("open_questions"), list):
            new_qs = [str(q) for q in gate["open_questions"] if str(q).strip()]
            if new_qs:
                plan["review_gate"]["open_questions"] = new_qs[:8]

    # scope refinements
    scope = groq_content.get("scope")
    if isinstance(scope, dict):
        if isinstance(scope.get("out_of_scope"), list):
            plan["scope"]["out_of_scope"] = [str(x) for x in scope["out_of_scope"] if str(x).strip()][:10]
        if isinstance(scope.get("in_scope"), list):
            additions = [str(x) for x in scope["in_scope"] if str(x).strip()]
            if additions:
                existing = {x.lower() for x in plan["scope"]["in_scope"]}
                for item in additions:
                    if item.lower() not in existing:
                        plan["scope"]["in_scope"].append(item)
                        existing.add(item.lower())

    # scenario prose, matched by id
    llm_scenarios = groq_content.get("test_scenarios")
    if isinstance(llm_scenarios, list):
        by_id = {s.get("id"): s for s in llm_scenarios if isinstance(s, dict) and s.get("id")}
        for scenario in plan["test_scenarios"]:
            incoming = by_id.get(scenario["id"])
            if not incoming:
                continue
            if isinstance(incoming.get("name"), str) and incoming["name"].strip():
                scenario["name"] = incoming["name"].strip()
            if isinstance(incoming.get("preconditions"), list):
                new_pre = [str(p) for p in incoming["preconditions"] if str(p).strip()]
                if new_pre:
                    scenario["preconditions"] = new_pre[:5]
            # the LLM may re-tag type/priority/maps_to within the allowed vocabulary
            if incoming.get("type") in {"positive", "negative", "boundary", "regression"}:
                scenario["type"] = incoming["type"]
            if incoming.get("priority") in {"P0", "P1", "P2"}:
                scenario["priority"] = incoming["priority"]
            if isinstance(incoming.get("maps_to"), str) and incoming["maps_to"].strip():
                scenario["maps_to"] = incoming["maps_to"].strip()[:30]
            tc_by_id = {
                tc.get("id"): tc
                for tc in incoming.get("test_cases", [])
                if isinstance(tc, dict) and tc.get("id")
            }
            for tc in scenario["test_cases"]:
                llm_tc = tc_by_id.get(tc["id"])
                if not llm_tc:
                    continue
                if isinstance(llm_tc.get("title"), str) and llm_tc["title"].strip():
                    tc["title"] = llm_tc["title"].strip()
                if isinstance(llm_tc.get("steps"), list):
                    steps = [str(s) for s in llm_tc["steps"] if str(s).strip()]
                    if steps:
                        tc["steps"] = steps[:10]
                if isinstance(llm_tc.get("expected"), str) and llm_tc["expected"].strip():
                    tc["expected"] = llm_tc["expected"].strip()
    return plan


# ---------------------------------------------------------------- validate
def validate(plan: dict) -> list[str]:
    """Return a list of structural problems (empty = valid)."""
    errors: list[str] = []
    if not isinstance(plan, dict):
        return ["plan is not an object"]
    for key in ("meta", "summary", "scope", "gap_analysis", "coverage_requirements",
                "test_scenarios", "status", "review_gate"):
        if key not in plan:
            errors.append(f"missing key: {key}")

    scenario_ids: set[str] = set()
    case_ids: set[str] = set()
    valid_priorities = {"P0", "P1", "P2"}
    valid_types = {"positive", "negative", "boundary", "regression", "functional", "smoke"}
    for scenario in plan.get("test_scenarios", []):
        sid = scenario.get("id", "")
        if not re.fullmatch(r"S-\d{2,}", str(sid)):
            errors.append(f"scenario id not S-XX: {sid!r}")
        scenario_ids.add(str(sid))
        if str(scenario.get("priority", "")) not in valid_priorities:
            errors.append(f"scenario {sid} priority not P0/P1/P2: {scenario.get('priority')!r}")
        if str(scenario.get("type", "")).lower() not in valid_types:
            errors.append(f"scenario {sid} type not recognized: {scenario.get('type')!r}")
        for tc in scenario.get("test_cases", []):
            tcid = tc.get("id", "")
            if not re.fullmatch(r"TC-\d{2,}", str(tcid)):
                errors.append(f"test case id not TC-XX: {tcid!r}")
            case_ids.add(str(tcid))

    for coverage in plan.get("coverage_requirements", []):
        for ref in coverage.get("test_cases", []):
            if ref not in case_ids:
                errors.append(f"coverage references unknown test case: {ref}")

    for gap in plan.get("gap_analysis", []):
        if not gap.get("area") or not gap.get("finding"):
            errors.append("gap_analysis entry missing area or finding")
    return errors


# ---------------------------------------------------------------- render
def to_markdown(plan: dict) -> str:
    """Render the plan dict as a professional markdown document."""
    meta = plan.get("meta", {})
    lines: list[str] = []
    add = lines.append

    status = plan.get("status", "DRAFT")
    add(f"# Test Plan — {meta.get('jira_id', '')}")
    add("")
    if status == "DRAFT":
        add("> ⛔ **Status: DRAFT — pending human review.** Not approved until a QA owner signs off.")
    else:
        add(f"> **Status:** {status}")
    add("")
    add(f"> **Engine:** {meta.get('engine', ENGINE)} · **Schema:** {meta.get('schema_version', '')}  ")
    add(f"> **Generated:** {meta.get('generated_at', '')} · **Model:** {meta.get('model', '')}  ")
    source = meta.get("source", {})
    add(f"> **Source:** {source.get('type', '')} · {source.get('status', '')} · Priority {source.get('priority', '')}")
    add("")

    mode = plan.get("generation", {}).get("mode", "groq")
    gen_error = plan.get("generation", {}).get("error")
    if mode != "groq" or gen_error:
        add("> ⚠️ **Note:** LLM enrichment was unavailable; this plan was generated "
            "from the deterministic engine. Run Groq Test Connection in Settings to enable AI content.")
        add("")

    add("## 1. Scope & Objectives")
    add("")
    add(plan.get("summary", ""))
    add("")
    scope = plan.get("scope", {})
    add("**In scope:**")
    for item in scope.get("in_scope", []):
        add(f"- {item}")
    if scope.get("out_of_scope"):
        add("")
        add("**Out of scope:**")
        for item in scope.get("out_of_scope", []):
            add(f"- {item}")
    add("")

    add("## 2. Gaps & Questions for the author")
    add("")
    add("| # | Area | Finding | Severity | Question to author |")
    add("|---|------|---------|----------|--------------------|")
    gaps = plan.get("gap_analysis", [])
    for idx, gap in enumerate(gaps, start=1):
        add(
            f"| {idx} | {_escape_table(gap.get('area', ''))} "
            f"| {_escape_table(gap.get('finding', ''))} "
            f"| {_escape_table(gap.get('severity', ''))} "
            f"| {_escape_table(gap.get('question', ''))} |"
        )
    add("")

    add("## 3. Test Scenarios")
    add("")
    add("| ID | Priority | Type | Scenario | Maps to |")
    add("|----|----------|------|----------|---------|")
    for scenario in plan.get("test_scenarios", []):
        add(
            f"| {scenario.get('id', '')} | {scenario.get('priority', '')} "
            f"| {_escape_table(scenario.get('type', ''))} "
            f"| {_escape_table(scenario.get('name', ''))} "
            f"| {_escape_table(scenario.get('maps_to', ''))} |"
        )
    add("")

    for scenario in plan.get("test_scenarios", []):
        add(f"### {scenario.get('id')} — {scenario.get('name')}")
        add("")
        add(
            f"**Priority:** {scenario.get('priority', '')} · "
            f"**Type:** {scenario.get('type', '')} · "
            f"**Maps to:** {scenario.get('maps_to', '')}"
        )
        pre = scenario.get("preconditions", [])
        if pre:
            add("")
            add("**Preconditions:**")
            for p in pre:
                add(f"- {p}")
        add("")
        add("| ID | Title | Steps | Expected Result |")
        add("|----|-------|-------|-----------------|")
        for tc in scenario.get("test_cases", []):
            steps = "<br>".join(
                f"{i}. {_strip_step_number(step)}"
                for i, step in enumerate(tc.get("steps", []), start=1)
            )
            add(
                f"| {tc.get('id', '')} | {_escape_table(tc.get('title', ''))} "
                f"| {_escape_table(steps)} | {_escape_table(tc.get('expected', ''))} |"
            )
        add("")

    add("## 4. Requirements Traceability")
    add("")
    add("| Requirement | Source | Test Cases |")
    add("|-------------|--------|-----------|")
    for cov in plan.get("coverage_requirements", []):
        cases = ", ".join(cov.get("test_cases", [])) or "—"
        add(
            f"| {_escape_table(cov.get('requirement', ''))} "
            f"| {_escape_table(cov.get('source', ''))} | {cases} |"
        )
    add("")

    risks = plan.get("risks", [])
    if risks:
        add("## 5. Risks & Assumptions")
        add("")
        for risk in risks:
            add(f"- {risk}")
        add("")

    add("## 6. Entry / Exit Criteria")
    add("")
    add("**Exit criteria:**")
    add("")
    add(plan.get("exit_criteria", ""))
    add("")

    add("---")
    add("## ⛔ HUMAN REVIEW GATE")
    add("")
    gate = plan.get("review_gate", {})
    assumptions = gate.get("assumptions", []) if isinstance(gate, dict) else []
    open_qs = gate.get("open_questions", []) if isinstance(gate, dict) else []
    add("**Assumptions made:**")
    if assumptions:
        for a in assumptions:
            add(f"- {a}")
    else:
        add("- None recorded.")
    add("")
    add("**Open questions blocking sign-off:**")
    if open_qs:
        for q in open_qs:
            add(f"- {q}")
    else:
        add("- None — no blocking gaps detected.")
    add("")
    add("> ▶ **Approve, or edit, before test cases are written / automation begins.**")
    add("")
    add(f"*Generated by {meta.get('engine', ENGINE)} · {meta.get('generated_at', '')}*")
    return "\n".join(lines)


def _escape_table(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def _strip_step_number(step: str) -> str:
    """Remove a leading 'N.' / 'N)' / 'N -' the LLM may have added to a step,
    since the renderer numbers steps itself."""
    text = str(step).strip()
    return re.sub(r"^\d+[.)]?\s*-?\s+", "", text, count=1)
