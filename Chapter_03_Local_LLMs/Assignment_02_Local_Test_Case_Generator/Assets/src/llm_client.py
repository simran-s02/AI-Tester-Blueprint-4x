"""LLM client: Ollama first, automatic Groq fallback when Ollama is unavailable."""

import requests

from config_store import read_config

GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class LLMError(Exception):
    """Raised when no provider can generate a response."""


def generate(prompt: str, provider: str | None = None) -> str:
    """Generate a response.

    `provider` may be "ollama" or "groq". If omitted, the stored setting is used;
    when the stored provider is unavailable, Groq is tried as fallback.
    """
    config = read_config()
    provider = (provider or config.get("provider", "ollama")).lower()

    if provider == "groq":
        return _generate_groq(prompt, config)

    # Default path: Ollama, with automatic Groq fallback.
    try:
        return _generate_ollama(prompt, config)
    except (LLMError, requests.RequestException) as ollama_err:
        try:
            return _generate_groq(prompt, config)
        except (LLMError, requests.RequestException) as groq_err:
            raise LLMError(
                f"Ollama failed ({ollama_err}); Groq fallback also failed ({groq_err})."
            ) from groq_err


def _generate_ollama(prompt: str, config: dict) -> str:
    url = config.get("ollama_url", "http://localhost:11434").rstrip("/") + "/api/generate"
    model = config.get("ollama_model", "gemma3:1b")
    try:
        resp = requests.post(
            url,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=120,
        )
    except requests.RequestException as exc:
        raise LLMError(f"Could not reach Ollama at {url}: {exc}") from exc

    if resp.status_code != 200:
        raise LLMError(f"Ollama returned HTTP {resp.status_code}: {resp.text[:200]}")

    data = resp.json()
    return data.get("response", "").strip()


def _generate_groq(prompt: str, config: dict) -> str:
    api_key = config.get("groq_api_key", "")
    if not api_key:
        raise LLMError("Groq API key is not configured. Add it in the Settings page.")
    try:
        resp = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a Senior QA Engineer."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
            },
            timeout=120,
        )
    except requests.RequestException as exc:
        raise LLMError(f"Could not reach Groq API: {exc}") from exc

    if resp.status_code == 401:
        raise LLMError("Groq authentication failed (401). Check the API key in Settings.")
    if resp.status_code != 200:
        raise LLMError(f"Groq returned HTTP {resp.status_code}: {resp.text[:200]}")

    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()
