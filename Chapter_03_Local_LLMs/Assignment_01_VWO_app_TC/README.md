# Assignment 01 — VWO App Test Case Generation

## Chapter 03 — Local LLMs

## 1. Assignment Overview

The objective of this assignment is to generate software test cases from a given product requirement using an LLM.

The target application is the **VWO Login Dashboard**.

**Requirement / PRD:**  
https://docs.google.com/document/d/1GsT57ocl4HaUCxNhBGVmwvLYh7R24gjVB_RDteltkF4/edit?usp=sharing

The assignment requires generating **at least 25 test cases** based on the supplied requirement.

---

## 2. Assignment Requirement

The original task specifies:

> Generate the test cases from the requirement using an open-source model (Ollama).

The expected local model is:

```text
gemma3:1b
```

Minimum required output:

```text
At least 25 test cases
```

The test cases should be derived from the provided VWO Login Dashboard requirements.

---

## 3. Requirement Source

The test cases are based on the **Product Requirements Document: VWO Login Dashboard**.

The PRD is treated as the source of truth for test-case generation.

---

## 4. Intended Technology Flow

```text
VWO Login Dashboard Requirement
              ↓
        Prompt / Input
              ↓
       Local LLM via Ollama
              ↓
          gemma3:1b
              ↓
       Generated Test Cases
              ↓
          QA Review
```

The assignment explores how an LLM can assist a QA engineer in converting requirements into structured test scenarios and test cases.

---

## 5. Model Used

### Intended Model

The assignment recommends using a local open-source model through Ollama:

```text
Ollama
  ↓
gemma3:1b
```

### Actual Model Used for Final Generation

The local `gemma3:1b` model was evaluated during the assignment. However, its output did not meet the required quality and reliability for the final test-case deliverable.

Therefore, **Claude Sonnet 5 was used for the final generation of the test cases**.

This is a deviation from the original assignment requirement and is documented here for transparency.

### Reason for the Deviation

The local model did not generate sufficiently reliable and comprehensive test cases for the required output. An alternative model was therefore used to produce a more usable final test-case set.

The assignment consequently demonstrates both:

- Evaluation of a local LLM for QA test generation.
- Practical model selection based on output quality.

---

## 6. Test Case Generation Objective

The goal was to generate at least **25 distinct test cases** covering the requirements of the VWO Login Dashboard.

The generated test cases should be based on the supplied requirements and avoid unsupported assumptions.

QA review should consider:

- Functional coverage
- Positive scenarios
- Negative scenarios
- Validation scenarios
- Boundary conditions where supported by the requirements
- Authentication scenarios where specified
- Error handling where specified
- Requirement traceability
- Duplicate scenario avoidance

---

## 7. Test Case Structure

The test cases are structured using fields such as:

| Field | Description |
|---|---|
| Test ID | Unique identifier |
| Description | Scenario being validated |
| Pre-conditions | Conditions required before execution |
| Steps | Actions required to execute the test |
| Expected Result | Expected application behavior |
| Priority | Business/functional priority |

Example structure:

```text
TC-001
    ↓
Description
    ↓
Pre-conditions
    ↓
Steps
    ↓
Expected Result
    ↓
Priority
```

---

## 8. QA Review

LLM-generated test cases are not treated as automatically correct.

A QA engineer should review the output for:

1. Requirement coverage.
2. Accuracy of expected results.
3. Validity of pre-conditions.
4. Correctness of test steps.
5. Duplicate scenarios.
6. Unsupported assumptions.
7. Missing negative scenarios.
8. Appropriate test priority.

The LLM acts as a test-design assistant; final validation remains with the QA engineer.

---

## 9. Local LLM Learning Outcome

Although Claude Sonnet 5 was used for the final test-case generation, evaluating `gemma3:1b` was still an important part of the exercise.

The assignment demonstrated that model selection affects the quality of structured QA output.

```text
Local LLM
   ↓
Local execution
   ↓
Privacy / reduced cloud dependency
   ↓
Model capability varies by model size and task
   ↓
Prompt quality + model capability
   ↓
Output quality
```

A smaller local model may require stronger prompting, output validation, regeneration, or a more capable model for complex QA tasks.

---

## 10. Intended vs Actual Workflow

| Area | Assignment Requirement | Actual Execution |
|---|---|---|
| Requirement source | VWO Login Dashboard PRD | VWO Login Dashboard PRD |
| Minimum test cases | 25 | 25+ |
| Intended runtime | Ollama | Ollama evaluated |
| Intended model | `gemma3:1b` | `gemma3:1b` evaluated |
| Final generation model | Local model | Claude Sonnet 5 |
| QA review | Required | Applied to generated output |

---

## 11. Evidence / Artefacts

Supporting files and screenshots should be stored under the assignment's `Artefacts` directory.

Actual assignment structure:

```text
Assignment_01_VWO_app_TC/
│
├── Artefacts/
│   ├── VWO_RICEPOT_Test_Case_Generation_Prompt.md
│   └── VWO_Login_Test_Cases.md
│
└── Assets/
    └── Product Requirements Document_ VWO Login Dashboard.pdf
```

The assignment artefacts are:

- `Artefacts/VWO_RICEPOT_Test_Case_Generation_Prompt.md` — prompt used for generating the VWO test cases.
- `Artefacts/VWO_Login_Test_Cases.md` — generated VWO login test cases.
- `Assets/Product Requirements Document_ VWO Login Dashboard.pdf` — requirement source / PRD.

The Google Docs requirement referenced in the assignment is also linked above for reference.

**Never commit API keys, passwords, tokens, `.env` files, or other confidential information.**

---

## 12. Key Learning

LLM-based test-case generation is not simply:

```text
Requirement → LLM → Test Cases
```

A reliable QA workflow is:

```text
Requirement Quality
        +
Prompt Quality
        +
Model Capability
        +
Output Validation
        +
QA Review
        ↓
Quality Test Cases
```

This assignment demonstrates how a QA engineer can evaluate an LLM, identify limitations, and make a practical model-selection decision rather than blindly accepting generated output.

---

## 13. Conclusion

The assignment explored the use of LLMs to convert product requirements into QA test cases.

The intended approach was:

```text
PRD
 ↓
Ollama
 ↓
gemma3:1b
 ↓
25+ Test Cases
```

The local model was evaluated but did not provide sufficiently reliable output for the final submission. Therefore, **Claude Sonnet 5 was used for the final test-case generation**.

This deviation is explicitly documented so that the repository accurately represents the actual implementation and learning process.
