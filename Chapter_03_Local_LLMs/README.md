# Chapter 03 — Local LLMs

This chapter is part of the **AI Tester Blueprint 4x** learning journey and focuses on understanding and applying **Local Large Language Models (LLMs)** to practical QA and software testing use cases.

## Objective

The objective of this chapter is to understand how Local LLMs can be used in QA workflows, explore tools such as Ollama, and build practical AI-assisted testing solutions.

The chapter includes hands-on assignments covering:

- Local LLM usage
- Ollama
- LLM-assisted test case generation
- Prompt engineering for QA
- Jira integration
- Streamlit-based AI applications
- Evaluation of LLM output quality

---

## Contents

### 1. Assignment 01 — VWO App Test Case Generation

**Folder:**

```text
Assignment_01_VWO_app_TC/
```

This assignment focuses on generating test cases from the **VWO Login Dashboard** requirements using an LLM.

The assignment required generating **at least 25 test cases** and explored the use of Ollama with the local `gemma3:1b` model.

The local model was evaluated during the exercise. Due to output-quality limitations, **Claude Sonnet 5 was used for the final test-case generation**.

For complete assignment details, requirements, artefacts, and the model evaluation, see:

```text
Assignment_01_VWO_app_TC/README.md
```

---

### 2. Assignment 02 — Local Test Case Generator

**Folder:**

```text
Assignment_02_Local_Test_Case_Generator/
```

This assignment focuses on building a practical **AI-powered Test Case Generator** that connects Jira requirements with an LLM.

The application integrates:

```text
Jira
  ↓
Jira REST API
  ↓
Requirement Extraction
  ↓
Prompt Template
  ↓
LLM
  ↓
Generated Test Cases
  ↓
Streamlit UI
```

The project explores:

- Jira REST API integration
- Ollama
- Local LLMs
- Gemma 3:1B
- Prompt engineering
- Streamlit
- Structured test-case generation
- LLM output validation
- QA review

For complete implementation details, architecture, screenshots, configuration, and execution instructions, see:

```text
Assignment_02_Local_Test_Case_Generator/README.md
```

---

## Chapter Learning Outcomes

By completing this chapter, I learned how to:

- Understand the concept of Local LLMs.
- Run and interact with LLMs using Ollama.
- Work with local models such as `gemma3:1b`.
- Apply LLMs to software testing and QA use cases.
- Design prompts for structured test-case generation.
- Evaluate the quality and limitations of LLM-generated test cases.
- Integrate Jira requirements with an AI-assisted QA workflow.
- Build a Streamlit-based test-case generation application.
- Understand the difference between using a local LLM and an external/cloud LLM.
- Apply QA validation to AI-generated test artefacts.

---

## Chapter Structure

```text
Chapter_03_Local_LLMs/
│
├── Assignment_01_VWO_app_TC/
│   ├── README.md
│   ├── Artefacts/
│   └── Assets/
│
└── Assignment_02_Local_Test_Case_Generator/
    ├── README.md
    ├── Artefacts/
    └── Assets/
```

---

## Key Takeaway

This chapter demonstrates the practical use of LLMs in QA — from experimenting with local models to building an AI-assisted application that can consume Jira requirements and generate structured test cases.

The assignments also highlight an important QA principle:

> **AI-generated test cases should be reviewed and validated by a QA engineer before being treated as final test artefacts.**
