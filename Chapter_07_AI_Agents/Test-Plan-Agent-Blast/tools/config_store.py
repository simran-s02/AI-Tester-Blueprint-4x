"""Settings persistence for the Test Plan Creator.

Reads/writes `.app_settings.json` (secrets, git-ignored) and merges any
`.env` variables as a fallback so credentials never live in code.

Keys:
    jira.base_url | jira.email | jira.api_token
    groq.api_key  | groq.model
"""

from __future__ import annotations

import json
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - dotenv is a dependency, but keep import safe
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_PATH = BASE_DIR / ".app_settings.json"
ENV_PATH = BASE_DIR / ".env"

DEFAULT_SETTINGS = {
    "jira": {
        "base_url": "",
        "email": "",
        "api_token": "",
        # Source of truth for issue lookup. "key" = fetch by Jira key (default).
        # "title" = fetch by issue summary text (JQL search), requires base_url+token.
        "issue_lookup_by": "key",
    },
    "groq": {
        "api_key": "",
        "model": "openai/gpt-oss-120b",
    },
    # When true, Generate falls back to the bundled DEMO-101 fixture when no
    # Jira credentials are configured (lets the full UI flow run offline).
    "demo_mode": True,
}

# .env fallback keys
_ENV_MAP = {
    ("jira", "base_url"): "JIRA_BASE_URL",
    ("jira", "email"): "JIRA_EMAIL",
    ("jira", "api_token"): "JIRA_API_TOKEN",
    ("groq", "api_key"): "GROQ_API_KEY",
    ("groq", "model"): "GROQ_MODEL",
}


def _deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def _load_env_fallbacks() -> dict:
    if load_dotenv:
        load_dotenv(ENV_PATH)
    env_settings = {}
    for (section, field), env_key in _ENV_MAP.items():
        value = os.getenv(env_key, "").strip()
        if value:
            env_settings.setdefault(section, {})[field] = value
    return env_settings


def load_settings() -> dict:
    """Return settings merged over defaults (saved JSON wins over .env)."""
    settings = _deep_merge(DEFAULT_SETTINGS, _load_env_fallbacks())
    if SETTINGS_PATH.exists():
        try:
            saved = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
            settings = _deep_merge(settings, saved)
        except (json.JSONDecodeError, OSError):
            pass
    return settings


def save_settings(settings: dict) -> None:
    """Persist settings to .app_settings.json (secrets stay out of git)."""
    merged = _deep_merge(load_settings(), settings)
    SETTINGS_PATH.write_text(
        json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def mask_settings(settings: dict) -> dict:
    """Return a copy with secret values masked for display."""
    masked = json.loads(json.dumps(settings))
    if masked.get("jira", {}).get("api_token"):
        masked["jira"]["api_token"] = "••••••••"
    if masked.get("groq", {}).get("api_key"):
        masked["groq"]["api_key"] = "••••••••"
    return masked


def is_configured(settings: dict) -> dict:
    """Return which integrations have the required values filled in."""
    jira = settings.get("jira", {})
    groq = settings.get("groq", {})
    return {
        "jira": bool(
            (jira.get("base_url") or "").strip()
            and (jira.get("api_token") or "").strip()
        ),
        "groq": bool((groq.get("api_key") or "").strip()),
    }
