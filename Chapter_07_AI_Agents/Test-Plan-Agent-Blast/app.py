"""Test Plan Creator — Streamlit UI (B.L.A.S.T. Navigation layer).

Pages:
- Generate: prompt like "Fetch this Jira and create a test plan" + issue key.
- Settings: Jira (URL/email/token) + Groq (key/model) with connection tests.

Run: streamlit run app.py
See architecture/SOP-04-ui-navigation.md.
"""

from __future__ import annotations

import re
from pathlib import Path

import streamlit as st

from tools import plan_engine
from tools.config_store import is_configured, load_settings, save_settings
from tools.groq_client import GroqClient, GroqError
from tools.jira_client import JiraClient, JiraError
from tools.orchestrator import run_to_markdown

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

DEFAULT_GROQ_MODELS = [
    "openai/gpt-oss-120b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]

st.set_page_config(
    page_title="Test Plan Creator",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("🧪 Test Plan Creator")
st.sidebar.caption("Fetch a Jira issue → generate a test plan (Groq-powered).")


# ---------------------------------------------------------------- utils
def _extract_jira_key(text: str) -> str | None:
    match = re.search(r"\b([A-Z][A-Z0-9_]*-\d+)\b", text or "")
    return match.group(1) if match else None


def _build_demo_plan() -> dict:
    """Run the full pipeline against the bundled DEMO-101 fixture."""
    import json

    fixture_path = Path(__file__).resolve().parent / "tools" / "fixtures" / "sample_issue.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    issue = JiraClient("demo", "demo", "demo")._normalize_issue(fixture, "DEMO-101")
    plan = plan_engine.build_skeleton(issue, model="deterministic (fixture)")
    errors = plan_engine.validate(plan)
    if errors:
        raise RuntimeError("Demo plan failed validation: " + "; ".join(errors))
    return {"plan": plan, "issue": issue, "markdown": plan_engine.to_markdown(plan), "demo": True}


@st.cache_resource
def _load_settings_cached():
    return load_settings()


def _save_settings_ui(values: dict) -> None:
    save_settings(values)
    _load_settings_cached.clear()


# ---------------------------------------------------------------- pages
def settings_page() -> None:
    st.header("⚙️ Settings")
    st.caption("Configure Jira and Groq. Credentials are stored in the local `.env` file (git-ignored).")

    current = _load_settings_cached()
    jira = current.get("jira", {})
    groq = current.get("groq", {})
    has_jira_token = bool((jira.get("api_token") or "").strip())
    has_groq_key = bool((groq.get("api_key") or "").strip())

    with st.form("settings_form"):
        st.subheader("Jira")
        jira_url = st.text_input(
            "Jira base URL",
            value=jira.get("base_url", ""),
            placeholder="https://your-domain.atlassian.net",
            help="Include https:// and do not add /rest/api — the app detects v3/v2.",
        )
        jira_email = st.text_input("Email", value=jira.get("email", ""))
        if has_jira_token:
            st.caption("✅ A Jira API token is saved. Enter a new one below only to replace it.")
        jira_token = st.text_input(
            "API token (leave blank to keep the saved one)",
            type="password",
            value="",
            placeholder="Enter a new token to replace the saved one",
            help="Jira API token (https://id.atlassian.com/manage-profile/security/api-tokens).",
        )
        clear_jira_token = st.checkbox("Clear the saved Jira token", value=False)
        lookup_mode = st.selectbox(
            "Issue lookup by",
            options=["key", "title"],
            index=0 if jira.get("issue_lookup_by", "key") != "title" else 1,
            help="'key' = fetch PROJ-123 directly. 'title' = JQL search by summary text (needs base URL + token).",
        )

        st.divider()
        st.subheader("GROQ")
        if has_groq_key:
            st.caption("✅ A GROQ API key is saved. Enter a new one below only to replace it.")
        groq_key = st.text_input(
            "GROQ API key (leave blank to keep the saved one)",
            type="password",
            value="",
            placeholder="Enter a new key to replace the saved one",
            help="Groq console: https://console.groq.com/keys",
        )
        clear_groq_key = st.checkbox("Clear the saved GROQ API key", value=False)
        model_options = list(dict.fromkeys([groq.get("model") or DEFAULT_GROQ_MODELS[0], *DEFAULT_GROQ_MODELS]))
        groq_model = st.selectbox(
            "Model",
            options=model_options,
            index=0,
            help="Open-weight 120B model requested. Test Connection lists models available to your key.",
        )

        submitted = st.form_submit_button("💾 Save Settings", type="primary")

    if submitted:
        new_values = {
            "jira": {"base_url": jira_url.strip(), "email": jira_email.strip(), "issue_lookup_by": lookup_mode},
            "groq": {"model": groq_model},
        }
        # Token semantics: blank + not-clear -> keep; typed -> replace; clear -> remove.
        if clear_jira_token:
            new_values["jira"]["api_token"] = ""
        elif jira_token.strip():
            new_values["jira"]["api_token"] = jira_token.strip()
        else:
            new_values["jira"]["api_token"] = jira.get("api_token", "")

        if clear_groq_key:
            new_values["groq"]["api_key"] = ""
        elif groq_key.strip():
            new_values["groq"]["api_key"] = groq_key.strip()
        else:
            new_values["groq"]["api_key"] = groq.get("api_key", "")

        _save_settings_ui(new_values)
        current = load_settings()  # refresh so the status line below is accurate
        jira, groq = current.get("jira", {}), current.get("groq", {})
        has_jira_token = bool((jira.get("api_token") or "").strip())
        has_groq_key = bool((groq.get("api_key") or "").strip())
        st.success("Settings saved to `.env`.")

    st.divider()
    st.subheader("Test connections")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔌 Test Jira Connection"):
            with st.spinner("Testing Jira…"):
                try:
                    result = JiraClient(jira_url.strip(), jira_email.strip(), jira_token.strip() or jira.get("api_token", "")).test_connection()
                    st.success(f"Jira OK — API v{result['version']}, logged in as **{result['user']}**.")
                except JiraError as exc:
                    st.error(f"Jira test failed: {exc.message}")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Jira test failed: {exc}")
    with c2:
        if st.button("🔌 Test GROQ Connection"):
            key = groq_key.strip() or groq.get("api_key", "")
            with st.spinner("Testing GROQ…"):
                try:
                    result = GroqClient(key, model=groq_model).test_connection()
                    available = result["available_models"]
                    st.success(
                        f"GROQ OK — {len(available)} models available"
                        + (" · your model **is available** ✅" if result["requested_model_available"] else "")
                    )
                    if available:
                        st.caption("Live models: " + ", ".join(available[:12]) + ("…" if len(available) > 12 else ""))
                except GroqError as exc:
                    st.error(f"GROQ test failed: {exc.message}")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"GROQ test failed: {exc}")

    st.divider()
    # Recompute from the (possibly just-refreshed) jira/groq values so the status
    # reflects what is actually saved after a Submit.
    jira_ok = bool((jira.get("base_url") or "").strip() and has_jira_token)
    groq_ok = has_groq_key
    st.caption(
        "Status: "
        + ("✅ Jira configured" if jira_ok else "❌ Jira not configured")
        + " · "
        + ("✅ GROQ configured" if groq_ok else "❌ GROQ not configured")
        + " · stored in `.env` (git-ignored)"
    )


def generate_page() -> None:
    st.header("🚀 Generate a Test Plan")
    st.caption('Give a prompt like "Fetch this Jira and create a test plan", and confirm the issue key below.')

    current = _load_settings_cached()
    configured = is_configured(current)
    demo_mode = bool(current.get("demo_mode", True))

    if not configured["jira"] and not demo_mode:
        st.warning("Jira is not configured yet. Go to **Settings** to add your Jira URL, email, and API token.")
    elif not configured["jira"] and demo_mode:
        st.info("⚠️ Jira is not configured — running in **demo mode** against the bundled `DEMO-101` sample. Add your Jira URL/email/token in **Settings** to fetch real tickets.")
    if not configured["groq"]:
        st.info("GROQ is not configured — the plan will be generated by the deterministic engine only. Add a GROQ key in Settings for AI-enriched prose.")

    prompt = st.text_area(
        "Your prompt",
        height=90,
        placeholder="Fetch this Jira and create a test plan.",
    )

    detected = _extract_jira_key(prompt)
    issue_key = st.text_input(
        "Jira issue key",
        value=detected or "",
        placeholder="PROJ-123 (or leave empty to use the demo issue in demo mode)",
        help="Auto-detected from the prompt if it contains a Jira key (e.g. PROJ-123).",
    )

    enable_llm = st.checkbox("Use GROQ to enrich the test plan prose", value=configured["groq"])

    if st.button("✨ Generate Test Plan", type="primary", disabled=not (issue_key or demo_mode)):
        # ---- resolve what to fetch ---------------------------------
        use_demo = False
        fetch_target = issue_key.strip()
        if not fetch_target:
            if demo_mode:
                use_demo = True
            else:
                st.error("Enter a Jira issue key (or include one in the prompt).")
                return

        # ---- run ----------------------------------------------------
        if use_demo:
            with st.spinner("Generating demo test plan from the bundled DEMO-101 sample…"):
                try:
                    result = _build_demo_plan()
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Demo plan failed: {exc}")
                    return
        else:
            # Real Jira fetch. If lookup is by title and the input is not a key,
            # do a JQL summary search and pick the top result.
            lookup_by = current.get("jira", {}).get("issue_lookup_by", "key")
            if lookup_by == "title" and not _extract_jira_key(fetch_target):
                with st.spinner(f"Searching Jira for issues matching '{fetch_target}'…"):
                    try:
                        client = JiraClient(
                            current["jira"].get("base_url", ""),
                            current["jira"].get("email", ""),
                            current["jira"].get("api_token", ""),
                        )
                        matches = client.fetch_issue_by_title(fetch_target, max_results=1)
                    except JiraError as exc:
                        st.error(f"**{exc.code}**: {exc.message}")
                        return
                if not matches:
                    st.error(f"No Jira issue found matching '{fetch_target}'.")
                    return
                fetch_target = matches[0]["key"]
            with st.spinner(f"Fetching {fetch_target} from Jira and generating the test plan…"):
                result = run_to_markdown(fetch_target, settings=current, enable_llm=enable_llm)
                result["demo"] = False
            if result["error"]:
                st.error(f"**{result['error']['code']}**: {result['error']['message']}")
                return

        plan = result["plan"]
        issue = result["issue"]
        md = result["markdown"]

        generation = plan.get("generation", {})
        if result.get("demo"):
            st.info("🧪 **Demo mode** — this plan was generated from the bundled sample issue, not a live Jira ticket.")
        elif generation.get("mode") != "groq":
            st.warning(
                "Deterministic engine only — GROQ enrichment was skipped or failed"
                + (f": {generation.get('error')}" if generation.get("error") else "")
                + ". The plan below is still complete and validated."
            )

        st.subheader(f"📋 Test Plan — {issue['key']}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Type", issue.get("type") or "—")
        c2.metric("Priority", issue.get("priority") or "—")
        c3.metric("Acceptance criteria", len(issue.get("acceptance_criteria") or []))
        c4.metric("Test cases", sum(len(s.get("test_cases", [])) for s in plan.get("test_scenarios", [])))

        st.markdown("#### Issue")
        st.write(issue.get("summary") or "*No summary*")
        st.caption(f"Status: {issue.get('status') or '—'} · Components: {', '.join(issue.get('components') or []) or '—'} · Labels: {', '.join(issue.get('labels') or []) or '—'}")
        if issue.get("linked_issues"):
            st.caption("Linked: " + ", ".join(f"{li['key']} ({li.get('link_type', '')})" for li in issue["linked_issues"]))

        st.divider()
        st.markdown(md)

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        out_path = OUTPUT_DIR / f"TestPlan_{issue['key']}.md"
        out_path.write_text(md, encoding="utf-8")
        st.download_button(
            "⬇️ Download Test Plan (.md)",
            data=md.encode("utf-8"),
            file_name=f"TestPlan_{issue['key']}.md",
            mime="text/markdown",
            type="primary",
        )
        st.caption(f"Also saved to `{out_path.relative_to(BASE_DIR)}`")


def demo_page() -> None:
    """Offline demo using the bundled fixture (no credentials needed)."""
    st.header("🧪 Demo — offline sample issue")
    st.caption("Runs the deterministic engine against the bundled `DEMO-101` fixture. No Jira or GROQ needed.")
    if st.button("Generate demo test plan", type="primary"):
        try:
            result = _build_demo_plan()
        except Exception as exc:  # noqa: BLE001
            st.error(f"Demo plan failed: {exc}")
            return
        st.markdown(result["markdown"])


# ---------------------------------------------------------------- nav
PAGES = {
    "Generate": generate_page,
    "Settings": settings_page,
    "Demo (offline)": demo_page,
}
page = st.sidebar.radio("Navigate", list(PAGES.keys()), index=0)
PAGES[page]()
