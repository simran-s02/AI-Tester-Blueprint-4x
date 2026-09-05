"""Groq LLM client — connection test + chat completion (JSON mode).

Resilient OpenAI-compatible wrapper around https://api.groq.com.
See architecture/SOP-02-groq-llm.md.
"""

from __future__ import annotations

import json
import re
from typing import Any, Optional

import requests

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
TIMEOUT_SECONDS = 60
DEFAULT_MODEL = "openai/gpt-oss-120b"


class GroqError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class GroqClient:
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        self.api_key = (api_key or "").strip()
        self.model = (model or "").strip() or DEFAULT_MODEL
        if not self.api_key:
            raise GroqError("config", "Groq API key is empty.")
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

    # ---- connection -------------------------------------------------
    def test_connection(self) -> dict:
        """Return {'ok': True, 'model': ..., 'available_models': [...]} or raise."""
        try:
            resp = self._session.get(
                f"{GROQ_BASE_URL}/models", timeout=TIMEOUT_SECONDS
            )
        except requests.RequestException as exc:
            raise GroqError("network", f"Could not reach Groq API: {exc}") from exc
        if resp.status_code in (401, 403):
            raise GroqError(
                "auth", "Groq authentication failed (401/403). Check the API key."
            )
        if resp.status_code != 200:
            raise GroqError(
                "http", f"Groq /models returned HTTP {resp.status_code}: {resp.text[:200]}"
            )
        data = resp.json()
        models = sorted(
            item.get("id", "") for item in data.get("data", []) if item.get("id")
        )
        return {
            "ok": True,
            "model": self.model,
            "available_models": models,
            "requested_model_available": self.model in models,
        }

    # ---- chat -------------------------------------------------------
    def chat_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
    ) -> dict:
        """Ask the model for a JSON object. Returns parsed dict, or raises GroqError.

        Tries strict JSON mode first. If the model fails strict validation
        (HTTP 400 json_validate_failed, common with very large prompts), retries
        once without response_format and salvages JSON from the response.
        """
        try:
            return self._chat_json_attempt(system_prompt, user_prompt, temperature, enforce_json=True)
        except GroqError as first_error:
            if first_error.code in ("json_mode_failed", "not_json_object"):
                try:
                    return self._chat_json_attempt(
                        system_prompt, user_prompt, temperature, enforce_json=False
                    )
                except GroqError:
                    raise first_error from None
            raise

    def _chat_json_attempt(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        enforce_json: bool,
    ) -> dict:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }
        if enforce_json:
            payload["response_format"] = {"type": "json_object"}
        try:
            resp = self._session.post(
                f"{GROQ_BASE_URL}/chat/completions",
                json=payload,
                timeout=TIMEOUT_SECONDS,
            )
        except requests.RequestException as exc:
            raise GroqError("network", f"Could not reach Groq chat API: {exc}") from exc
        if resp.status_code in (401, 403):
            raise GroqError(
                "auth", "Groq authentication failed (401/403). Check the API key."
            )
        if resp.status_code == 404 and "model" in (resp.text or "").lower():
            raise GroqError(
                "model",
                f"Model '{self.model}' was not found on your Groq account. "
                "Run Test Groq Connection to see available models.",
            )
        if resp.status_code == 400 and "json_validate_failed" in (resp.text or ""):
            # Strict JSON mode rejected the generation — caller may retry without it.
            raise GroqError("json_mode_failed", "Strict JSON mode validation failed.")
        if resp.status_code != 200:
            raise GroqError(
                "http",
                f"Groq chat returned HTTP {resp.status_code}: {resp.text[:300]}",
            )
        data = resp.json()
        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        if not content:
            raise GroqError("empty", "Groq returned an empty completion.")
        return self._parse_json_content(content)

    @staticmethod
    def _parse_json_content(content: str) -> dict:
        text = content.strip()
        fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
        if fence:
            text = fence.group(1)
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            # try to salvage a JSON object from the response
            start, end = text.find("{"), text.rfind("}")
            if start != -1 and end > start:
                try:
                    parsed = json.loads(text[start : end + 1])
                except json.JSONDecodeError as exc:
                    raise GroqError(
                        "parse", f"Groq response was not valid JSON: {exc}"
                    ) from exc
            else:
                raise GroqError("parse", "Groq response was not valid JSON.")
        if not isinstance(parsed, dict):
            raise GroqError(
                "not_json_object",
                "Groq response was not a JSON object (strict JSON mode).",
            )
        return parsed
