"""Orchestrator — thin Navigation between tools (B.L.A.S.T. Layer 2).

Runs: settings -> Jira fetch/normalize -> deterministic skeleton -> Groq
prose (optional) -> validate -> test plan dict. Exposes a CLI too:
    python -m tools.orchestrator PROJ-123
See architecture/SOP-04-ui-navigation.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from tools.config_store import load_settings
from tools.groq_client import DEFAULT_MODEL, GroqClient, GroqError
from tools.jira_client import JiraClient, JiraError
from tools.plan_engine import (
    build_skeleton,
    merge_groq_content,
    to_markdown,
    validate,
)

GROQ_SYSTEM_PROMPT = """You are an expert QA test-plan writer following the STLC test-planning
skill. You receive a Jira issue and a deterministic DRAFT test-plan skeleton (ids S-01/TC-01,
gap analysis, traceability). Your ONLY job is to improve the human-readable PROSE and sharpen
the analysis. Return a SINGLE JSON object with EXACTLY these keys (do not echo the issue or
the full skeleton):

{
  "summary": "one crisp, professional paragraph describing the test objective",
  "scope": {"in_scope": ["..."], "out_of_scope": ["..."]},
  "gap_analysis": [
    {"area": "Functional", "finding": "what is missing or ambiguous",
     "severity": "✅ present | ⚠️ ambiguous | ❌ missing",
     "question": "one specific question for the ticket author"}
  ],
  "test_scenarios": [
    {
      "id": "S-01",
      "name": "clearer scenario name (keep the same id as the skeleton)",
      "type": "positive | negative | boundary | regression",
      "priority": "P0 | P1 | P2",
      "maps_to": "AC-1 | summary | gap",
      "preconditions": ["..."],
      "test_cases": [
        {
          "id": "TC-01",
          "title": "clearer case title (keep the same id)",
          "steps": ["concrete action without a leading number", "..."],
          "expected": "precise, observable expected result"
        }
      ]
    }
  ],
  "risks": ["realistic QA risk", "..."],
  "exit_criteria": "crisp QA exit criteria",
  "review_gate": {
    "assumptions": ["what you assumed"],
    "open_questions": ["questions blocking sign-off"]
  }
}

RULES:
- Map your output onto the skeleton ids: every id you return MUST exist in the skeleton,
  and every skeleton scenario/case must appear in your output.
- Never change structure, ids, counts, or acceptance criteria. Never fabricate requirements.
- Sharpen the gap_analysis with real QA insight, but keep each finding traceable to the ticket.
- Scenario priority uses the STLC risk model: P0 must-test, P1 should-test, P2 best-effort."""


# Compact shape reminder appended to the user prompt so large skeletons do not
# make the model lose the required output contract.
GROQ_OUTPUT_SHAPE = """
Return ONLY a JSON object shaped exactly like:
{"summary": str, "scope": {"in_scope": [str], "out_of_scope": [str]},
 "gap_analysis": [{"area": str, "finding": str, "severity": str, "question": str}],
 "test_scenarios": [{"id": "S-XX", "name": str, "type": str, "priority": "P0|P1|P2",
   "maps_to": str, "preconditions": [str],
   "test_cases": [{"id": "TC-XX", "title": str, "steps": [str], "expected": str}]}],
 "risks": [str], "exit_criteria": str,
 "review_gate": {"assumptions": [str], "open_questions": [str]}}
Do NOT include the issue or skeleton objects in your reply."""


class OrchestratorError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def run(issue_key: str, settings: Optional[dict] = None, enable_llm: bool = True) -> dict:
    """Fetch issue and produce a validated test plan dict.

    Returns {'plan': {...}, 'issue': {...}, 'error': None} on success or
    {'plan': None, 'issue': None, 'error': {'code', 'message'}} on failure.
    """
    settings = settings or load_settings()
    issue_key = issue_key.strip()
    if not issue_key:
        return _error("bad_key", "No Jira issue key provided.")

    try:
        # ---- 1) fetch + normalize (Link layer) ---------------------
        jira_cfg = settings.get("jira", {})
        client = JiraClient(
            jira_cfg.get("base_url", ""),
            jira_cfg.get("email", ""),
            jira_cfg.get("api_token", ""),
        )
        issue = client.fetch_issue(issue_key)
        if not (issue.get("summary") or "").strip() and not issue.get("acceptance_criteria"):
            return _error(
                "empty_issue",
                f"Issue {issue_key} has no summary and no acceptance criteria — "
                "cannot build a meaningful test plan.",
            )

        # ---- 2) deterministic skeleton -----------------------------
        groq_cfg = settings.get("groq", {})
        model = (groq_cfg.get("model") or "").strip() or DEFAULT_MODEL
        skeleton = build_skeleton(issue, model=model)

        # ---- 3) LLM prose refinement (optional, resilient) ---------
        groq_content = None
        llm_error = None
        if enable_llm and (groq_cfg.get("api_key") or "").strip():
            try:
                groq_client = GroqClient(groq_cfg["api_key"], model=model)
                user_payload = {
                    "issue": {
                        "key": issue["key"],
                        "type": issue["type"],
                        "summary": issue["summary"],
                        "description_md": issue["description_md"][:4000],
                        "acceptance_criteria": issue["acceptance_criteria"],
                        "linked_issues": issue["linked_issues"],
                    },
                    "skeleton": skeleton,
                }
                groq_content = groq_client.chat_json(
                    system_prompt=GROQ_SYSTEM_PROMPT,
                    user_prompt=(
                        "Refine the prose of this test plan. "
                        + GROQ_OUTPUT_SHAPE
                        + "\n\nContext (issue + skeleton to refine):\n"
                        + json.dumps(user_payload, indent=2)[:30000]
                    ),
                )
                skeleton = merge_groq_content(skeleton, groq_content)
            except (GroqError, Exception) as exc:  # noqa: BLE001 - resilient fallback
                llm_error = getattr(exc, "message", None) or str(exc)
                skeleton["generation"]["mode"] = "fallback"
                skeleton["generation"]["error"] = llm_error

        # ---- 4) validate -------------------------------------------
        errors = validate(skeleton)
        if errors:
            return _error("validation", "Test plan failed validation: " + "; ".join(errors))

        return {"plan": skeleton, "issue": issue, "error": None}
    except JiraError as exc:
        return _error(exc.code, exc.message)
    except Exception as exc:  # noqa: BLE001 - last-resort guard for the UI
        return _error("unexpected", f"Unexpected error: {exc}")


def run_to_markdown(issue_key: str, settings: Optional[dict] = None, enable_llm: bool = True) -> dict:
    result = run(issue_key, settings, enable_llm)
    if result["error"]:
        return result
    result["markdown"] = to_markdown(result["plan"])
    return result


def _error(code: str, message: str) -> dict:
    return {"plan": None, "issue": None, "error": {"code": code, "message": message}}


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a test plan from a Jira issue key.")
    parser.add_argument("issue_key", help="e.g. PROJ-123")
    parser.add_argument("--no-llm", action="store_true", help="Skip Groq enrichment.")
    parser.add_argument("--out", type=Path, default=None, help="Write .md to this path.")
    args = parser.parse_args(argv)

    result = run_to_markdown(args.issue_key, enable_llm=not args.no_llm)
    if result["error"]:
        print(f"ERROR [{result['error']['code']}]: {result['error']['message']}", file=sys.stderr)
        return 1

    md = result["markdown"]
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(md, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
