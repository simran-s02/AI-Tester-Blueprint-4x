"""Jira Test Case Generator — main chat screen.

User types "create test cases for JIRA-102"; the app parses the ticket key,
fetches the ticket, merges it into the testcase_creator template, and renders
the generated test cases in the chat.
"""

import re
from pathlib import Path

import streamlit as st

from config_store import read_config
from jira_client import JiraError, TICKET_KEY_RE, fetch_ticket
from llm_client import LLMError, generate

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR.parent / "templates" / "testcase_creator.md"

DEFAULT_NUM_CASES = 10
MAX_NUM_CASES = 20

st.set_page_config(page_title="Jira Test Case Generator", page_icon="🧪")
st.title("🧪 Jira Test Case Generator")


def load_template() -> str:
    return TEMPLATE_PATH.read_text(encoding="utf-8")


def build_prompt(ticket: dict, num_cases: int) -> str:
    template = load_template()
    requirements = (
        f"Ticket: {ticket['key']} — {ticket['summary']}\n\n"
        f"Description:\n{ticket['description'] or 'Not specified'}\n\n"
        f"Acceptance Criteria:\n{ticket['acceptance_criteria'] or 'Not specified'}"
    )
    prompt = template.replace("[PASTE REQUIREMENTS HERE]", requirements)
    prompt = re.sub(r"\[NUMBER\]", str(num_cases), prompt)
    return prompt


def parse_ticket_key(message: str) -> str | None:
    match = re.search(TICKET_KEY_RE, message)
    return match.group(0) if match else None


def extract_num_cases(message: str) -> int:
    """Reads "N test cases" / "N cases" from the message; defaults to 10."""
    match = re.search(r"(\d+)\s+(?:test\s+)?cases?", message, re.IGNORECASE)
    num = int(match.group(1)) if match else DEFAULT_NUM_CASES
    return max(1, min(num, MAX_NUM_CASES))


def add_assistant_message(text: str, provider_used: str | None = None):
    label = f"**{provider_used}**" if provider_used else "**Assistant**"
    st.chat_message("assistant").markdown(f"{label}\n\n{text}")


# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Type a message… e.g. \"create 12 test cases for JIRA-102\"")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    ticket_key = parse_ticket_key(prompt)
    if not ticket_key:
        response = (
            "I couldn't find a Jira ticket key in your message. "
            "Try something like: `create test cases for JIRA-102`"
        )
        st.session_state.messages.append({"role": "assistant", "content": response})
        add_assistant_message(response)
    else:
        num_cases = extract_num_cases(prompt)
        config = read_config()
        provider = config.get("provider", "ollama")

        # Note the provider *before* generation so we can show which one produced the output.
        with st.status(f"Generating test cases for **{ticket_key}**…", expanded=True) as status:
            try:
                st.write("Fetching ticket from Jira…")
                ticket = fetch_ticket(ticket_key)
                st.write(f"Fetched **{ticket['key']}**: {ticket['summary'] or '(no summary)'}")

                st.write("Building prompt from template…")
                prompt_text = build_prompt(ticket, num_cases)

                st.write(f"Calling **{provider}**…")
                result = generate(prompt_text, provider=provider)
                status.update(label=f"Generated {num_cases} test cases for **{ticket_key}**", state="complete")
            except (JiraError, LLMError) as exc:
                status.update(label="Generation failed", state="error")
                st.session_state.messages.append({"role": "assistant", "content": str(exc)})
                add_assistant_message(str(exc))
            else:
                st.session_state.messages.append(
                    {"role": "assistant", "content": f"({provider})\n\n{result}"}
                )
                add_assistant_message(result, provider_used=provider)
