# Taste

## Workflow & communication

- Wants the agent to run the app locally and verify it actually works before finishing — not just deliver code. Confidence: 0.8
- Uses a plan document (e.g., `plan.md`) as the source of truth for implementation and expects the agent to follow it rather than inventing requirements. Confidence: 0.7
- Prefers to create and manage the `.env` / secrets file himself; the agent should read and respect the user-provided `.env` instead of creating or populating it. Confidence: 0.6
