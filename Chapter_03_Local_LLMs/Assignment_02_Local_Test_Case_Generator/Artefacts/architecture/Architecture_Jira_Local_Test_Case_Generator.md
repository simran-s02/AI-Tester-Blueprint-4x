# Architecture — Jira Local Test Case Generator

## High-Level Architecture

```text
                           ┌──────────────────────┐
                           │        USER          │
                           │  Create test cases   │
                           │      for KAN-1       │
                           └──────────┬───────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │     STREAMLIT UI      │
                           │        app.py         │
                           └──────────┬───────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │     JIRA CLIENT       │
                           │   jira_client.py      │
                           └──────────┬───────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │     JIRA REST API     │
                           │     QA_Testing        │
                           │        KAN-1          │
                           └──────────┬───────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │  REQUIREMENT DATA     │
                           │  • Summary            │
                           │  • Description        │
                           │  • Acceptance Criteria│
                           └──────────┬───────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │   PROMPT TEMPLATE     │
                           │ testcase_creator.md   │
                           └──────────┬───────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │      LLM CLIENT       │
                           │    llm_client.py      │
                           └──────────┬───────────┘
                                      │
                         ┌────────────┴────────────┐
                         │                         │
                         ▼                         ▼
                ┌──────────────────┐      ┌──────────────────┐
                │      OLLAMA      │      │       GROQ       │
                │  Local LLM       │      │  Cloud/API LLM   │
                │  gemma3:1b       │      │   (Alternative)  │
                │ localhost:11434  │      │                  │
                └────────┬─────────┘      └────────┬─────────┘
                         │                         │
                         └────────────┬────────────┘
                                      ▼
                           ┌──────────────────────┐
                           │  GENERATED TEST CASES │
                           │    Markdown Table     │
                           └──────────┬───────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │     STREAMLIT UI      │
                           │   Formatted Output    │
                           └──────────────────────┘
```

## Component Responsibilities

| Component | File / Service | Responsibility |
|---|---|---|
| User Interface | `app.py` | Accepts the user's request and displays generated test cases |
| Jira Integration | `jira_client.py` | Connects to Jira REST API and retrieves ticket details |
| Configuration | `config.py`, `config_store.py` | Handles application configuration |
| Prompt Template | `templates/testcase_creator.md` | Defines rules and format for test-case generation |
| LLM Integration | `llm_client.py` | Sends prompts to the configured LLM provider |
| Local LLM | Ollama | Runs the local `gemma3:1b` model |
| Alternative LLM | Groq | Provides an optional cloud/API-based LLM |
| Output | Streamlit Markdown | Displays generated test cases as a structured table |

## End-to-End Data Flow

```text
User request
    ↓
Identify Jira issue key
    ↓
Jira REST API
    ↓
Retrieve ticket details
    ↓
Extract Summary / Description / Acceptance Criteria
    ↓
Apply testcase_creator.md prompt
    ↓
Send prompt to selected LLM
    ↓
Generate test cases
    ↓
Display Markdown table in Streamlit
```

## Local LLM Flow

```text
Streamlit Application
        ↓
http://localhost:11434
        ↓
      Ollama
        ↓
   gemma3:1b
        ↓
Generated test cases
        ↓
Streamlit Application
```

## Jira Integration Flow

```text
Streamlit
    ↓
jira_client.py
    ↓
Jira REST API
    ↓
QA_Testing
    ↓
KAN-1
    ↓
Summary
Description
Acceptance Criteria
```

## Prompt Engineering Flow

```text
Jira Requirements
       ↓
testcase_creator.md
       ↓
QA role + requested count
       ↓
Required table structure
       ↓
Test ID / Priority rules
       ↓
Requirement-only generation
       ↓
Anti-hallucination rules
       ↓
LLM
       ↓
Structured test cases
```

## Configuration Flow

```text
Application Configuration
        │
        ├── Jira URL
        ├── Jira Email
        ├── Jira API Token
        │
        ├── Ollama URL
        ├── Ollama Model
        │
        └── Groq API Key
```

Sensitive credentials should remain local and must not be committed to GitHub.

## Overall Architecture Summary

```text
Jira Requirement
      ↓
Jira REST API
      ↓
Requirement Extraction
      ↓
Prompt Template
      ↓
LLM
      ↓
Test Case Generation
      ↓
Markdown Table
      ↓
Streamlit UI
      ↓
QA Review
```

**Primary local-LLM path:**

```text
Jira → Streamlit → Jira REST API → Prompt → Ollama → Gemma 3:1B → Test Cases
```

An optional Groq integration provides an alternative LLM provider.
