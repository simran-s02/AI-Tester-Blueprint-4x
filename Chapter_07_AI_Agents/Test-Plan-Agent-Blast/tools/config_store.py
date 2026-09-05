"""Settings persistence for the Test Plan Creator.

Single source of truth: the local `.env` file (git-ignored). No secondary
`.app_settings.json` store, so a freshly edited `.env` can never be silently
overridden by a stale JSON snapshot.

On first load after this change, any existing `.app_settings.json` values are
migrated into `.env` and the JSON file is removed.

Keys:
    jira.base_url | jira.email | jira.api_token
    groq.api_key  | groq.model
"""

from __future__ import annotations

import json
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

# internal key -> .env variable name
_ENV_MAP: dict[tuple[str, str], str] = {
    ("jira", "base_url"): "JIRA_BASE_URL",
    ("jira", "email"): "JIRA_EMAIL",
    ("jira", "api_token"): "JIRA_API_TOKEN",
    ("groq", "api_key"): "GROQ_API_KEY",
    ("groq", "model"): "GROQ_MODEL",
}
# reverse: env var -> (section, field)
_ENV_REVERSE = {v: k for k, v in _ENV_MAP.items()}


def _deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


# ---------------------------------------------------------------- .env IO
def _read_env_file() -> dict:
    """Parse .env into {KEY: value} (last occurrence wins)."""
    values: dict[str, str] = {}
    if not ENV_PATH.exists():
        return values
    try:
        text = ENV_PATH.read_text(encoding="utf-8")
    except OSError:
        return values
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, raw = line.partition("=")
        key = key.strip()
        raw = raw.strip()
        if (raw.startswith('"') and raw.endswith('"')) or (
            raw.startswith("'") and raw.endswith("'")
        ):
            raw = raw[1:-1]
        values[key] = raw
    return values


def _load_env_fallbacks() -> dict:
    """Load .env into the settings dict shape.

    The `.env` file is the single source of truth; we deliberately do NOT fall
    back to os.getenv, because load_dotenv may have cached a stale value in the
    process environment after a clear/edit.
    """
    if load_dotenv:
        load_dotenv(ENV_PATH, override=True)
    file_values = _read_env_file()
    settings: dict = {}
    for (section, field), env_key in _ENV_MAP.items():
        value = file_values.get(env_key)
        if value is not None and str(value).strip():
            settings.setdefault(section, {})[field] = str(value).strip()
    return settings


# ---------------------------------------------------------------- migration
def _migrate_legacy_json() -> None:
    """One-time import of a legacy .app_settings.json into .env, then remove it."""
    if not SETTINGS_PATH.exists():
        return
    try:
        legacy = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        legacy = None
    if not isinstance(legacy, dict):
        return
    updates: dict[str, dict] = {}
    for (section, field), env_key in _ENV_MAP.items():
        value = legacy.get(section, {}).get(field)
        if value not in (None, ""):
            updates.setdefault(section, {})[field] = str(value)
    if updates:
        merged = _deep_merge(_load_env_fallbacks(), updates)
        # flat env map for writer
        flat = {env_key: merged.get(section, {}).get(field, "") for (section, field), env_key in _ENV_MAP.items()}
        _write_env_values_flat(flat)
    try:
        SETTINGS_PATH.unlink()
    except OSError:
        pass


def _write_env_values_flat(flat: dict[str, str]) -> None:
    """Write a flat {ENV_KEY: value} map to .env, preserving comments."""
    known_keys = list(_ENV_REVERSE.keys())
    lines_out: list[str] = []
    seen: set[str] = set()
    existing = ENV_PATH.read_text(encoding="utf-8").splitlines() if ENV_PATH.exists() else []
    for line in existing:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            lines_out.append(line)
            continue
        key = stripped.partition("=")[0].strip()
        if key in _ENV_REVERSE:
            new_value = flat.get(key)
            if new_value:
                lines_out.append(f"{key}={new_value}")
            seen.add(key)
    for key in known_keys:
        if key in seen:
            continue
        if flat.get(key):
            lines_out.append(f"{key}={flat[key]}")
    ENV_PATH.write_text("\n".join(lines_out) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- public API
def load_settings() -> dict:
    """Return effective settings. Order: defaults < .env (no JSON override)."""
    _migrate_legacy_json()
    return _deep_merge(DEFAULT_SETTINGS, _load_env_fallbacks())


def save_settings(settings: dict) -> None:
    """Persist settings to .env (the single source of truth)."""
    current = load_settings()
    merged = _deep_merge(current, settings)
    flat: dict[str, str] = {}
    for (section, field), env_key in _ENV_MAP.items():
        value = merged.get(section, {}).get(field)
        flat[env_key] = "" if value is None else str(value)
    _write_env_values_flat(flat)


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
