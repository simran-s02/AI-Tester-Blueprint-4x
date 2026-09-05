# SOP-02 — Groq LLM Integration

**Layer:** 3 (Tools) · **Module:** `tools/groq_client.py` · **Status:** Implemented

## Goal
Provide a resilient, OpenAI-compatible chat interface to **Groq** (`https://api.groq.com`) for generating test-plan prose, plus a **connection test** that lists live models.

## Input
- `api_key`, `model` (from settings)

## Behavior
1. **Connection test:** `GET https://api.groq.com/openai/v1/models` with `Authorization: Bearer {key}`. On success return model ids (sorted); on 401 raise `GroqError("auth")`.
2. **Chat:** `POST https://api.groq.com/openai/v1/chat/completions`
   - `messages`: system (deterministic instructions) + user (JSON payload to enrich)
   - `response_format={"type":"json_object"}` (Groq supports JSON mode)
   - `temperature=0.3` for reproducibility
   - Do **not** send model-specific params (reasoning_effort etc.) — keep conservative so any model works.
3. Parse `choices[0].message.content` as JSON. If the model wraps content in ```json fences, strip them. On any parse failure, return an error marker so `plan_engine` can fall back.

## Resilience (verified live 2026-09-05)
- `chat_json` first requests strict JSON mode (`response_format={"type":"json_object"}`).
- Some models (incl. `openai/gpt-oss-120b`) fail strict validation on **very large prompts**
  (HTTP 400 `json_validate_failed`). `chat_json` detects that specific error and **retries once
  without `response_format`**, then salvages JSON from the response (fence-strip → parse → substring).
- This keeps the deterministic-skeleton fallback as the last line of defense.

## Edge Cases
- Missing key → raise before network call.
- Model not available on the account → error surfaced; user picks another from the live model list.
- Rate limit / 5xx → error marker → orchestrator uses deterministic fallback plan.
- Model returns non-JSON → strip fences, retry parse once, else error marker.

## Golden Rule
If Groq call logic changes, update this SOP first, then the code.
