"""Settings screen: edit and persist Jira + LLM credentials and provider choice."""

import streamlit as st

from config_store import read_config, write_config
from jira_client import JiraError, fetch_ticket
from llm_client import LLMError, generate

st.set_page_config(page_title="Settings", page_icon="⚙️")
st.title("⚙️ Settings")

config = read_config()

with st.form("settings_form"):
    st.subheader("Jira")
    jira_url = st.text_input("Jira base URL", value=config.get("jira_url", ""),
                             placeholder="https://your-domain.atlassian.net")
    jira_email = st.text_input("Jira email", value=config.get("jira_email", ""))
    jira_api_token = st.text_input(
        "Jira API token",
        value=config.get("jira_api_token", ""),
        type="password",
        help="Atlassian API token (not your password).",
    )

    st.subheader("LLM Provider")
    provider = st.radio(
        "Default provider",
        options=["ollama", "groq"],
        index=0 if config.get("provider", "ollama") == "ollama" else 1,
        format_func=lambda p: "Ollama (local, default)" if p == "ollama" else "Groq (cloud)",
        help="Ollama is tried first; Groq is the automatic fallback when Ollama is unavailable.",
    )
    ollama_url = st.text_input("Ollama URL", value=config.get("ollama_url", "http://localhost:11434"))
    ollama_model = st.text_input("Ollama model", value=config.get("ollama_model", "gemma3:1b"))
    groq_api_key = st.text_input("Groq API key", value=config.get("groq_api_key", ""), type="password")

    saved = st.form_submit_button("Save settings")

if saved:
    write_config(
        {
            "jira_url": jira_url,
            "jira_email": jira_email,
            "jira_api_token": jira_api_token,
            "provider": provider,
            "ollama_url": ollama_url,
            "ollama_model": ollama_model,
            "groq_api_key": groq_api_key,
        }
    )
    st.success("Settings saved.")

st.divider()
st.subheader("Test connections")

col1, col2 = st.columns(2)
with col1:
    if st.button("Test Jira connection", type="primary"):
        with st.spinner("Fetching a sample ticket…"):
            try:
                ticket = fetch_ticket("KAN-1")
                st.success(f"Jira OK — fetched KAN-1: {ticket['summary']}")
            except JiraError as exc:
                st.error(f"Jira connection failed: {exc}")
with col2:
    if st.button("Test LLM connection"):
        with st.spinner("Generating a short reply…"):
            try:
                result = generate("Reply with exactly: OK")
                st.success(f"LLM OK — response: {result[:120]}")
            except LLMError as exc:
                st.error(f"LLM connection failed: {exc}")
