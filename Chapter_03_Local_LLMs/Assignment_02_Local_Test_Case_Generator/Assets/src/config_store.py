"""Config store: .env seeds initial values, config.json is the runtime store.

The Settings screen reads/writes config.json; values are never hardcoded.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"

# Keys persisted in config.json
CONFIG_KEYS = [
    "jira_url",
    "jira_email",
    "jira_api_token",
    "provider",  # "ollama" | "groq"
    "groq_api_key",
    "ollama_url",
    "ollama_model",
]

# .env names mapped to config keys (used only as initial seeds)
_ENV_MAP = {
    "JIRA_URL": "jira_url",
    "JIRA_EMAIL": "jira_email",
    "JIRA_API_TOKEN": "jira_api_token",
    "GROQ_API_TOKEN": "groq_api_key",
    "OLLAMA_URL": "ollama_url",
    "OLLAMA_MODEL": "ollama_model",
}


def _load_env():
    load_dotenv(BASE_DIR / ".env")


def _seeded_defaults():
    _load_env()
    return {
        "jira_url": os.getenv("JIRA_URL", ""),
        "jira_email": os.getenv("JIRA_EMAIL", ""),
        "jira_api_token": os.getenv("JIRA_API_TOKEN", ""),
        "provider": os.getenv("LLM_PROVIDER", "ollama"),
        "groq_api_key": os.getenv("GROQ_API_TOKEN", ""),
        "ollama_url": os.getenv("OLLAMA_URL", "http://localhost:11434"),
        "ollama_model": os.getenv("OLLAMA_MODEL", "gemma3:1b").strip('"'),
    }


def read_config() -> dict:
    """Return runtime config, merged over .env-seeded defaults."""
    config = _seeded_defaults()
    if CONFIG_PATH.exists():
        try:
            saved = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(saved, dict):
                for key in CONFIG_KEYS:
                    if saved.get(key):
                        config[key] = saved[key]
        except (json.JSONDecodeError, OSError):
            pass  # fall back to .env seeds on a corrupt/unreadable config
    return config


def write_config(updates: dict) -> dict:
    """Persist updates to config.json (runtime store) and return the merged config."""
    config = read_config()
    for key in CONFIG_KEYS:
        if key in updates and updates[key] is not None:
            config[key] = str(updates[key]).strip()
    CONFIG_PATH.write_text(
        json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return config
