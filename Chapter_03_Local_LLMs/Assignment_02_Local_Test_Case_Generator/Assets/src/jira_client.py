"""Jira REST API client: fetch ticket details for test case generation."""

import requests

from config_store import read_config

TICKET_KEY_RE = r"\b[A-Z]+-\d+\b"


class JiraError(Exception):
    """Raised when a ticket cannot be fetched."""


def fetch_ticket(key: str) -> dict:
    """Fetch a ticket and return {key, summary, description, acceptance_criteria}."""
    config = read_config()
    jira_url = config.get("jira_url", "").rstrip("/")
    if not jira_url or not config.get("jira_email") or not config.get("jira_api_token"):
        raise JiraError("Jira credentials are not configured. Open the Settings page first.")

    url = f"{jira_url}/rest/api/2/issue/{key}"
    try:
        resp = requests.get(
            url,
            auth=(config["jira_email"], config["jira_api_token"]),
            headers={"Accept": "application/json"},
            timeout=30,
        )
    except requests.RequestException as exc:
        raise JiraError(f"Could not reach Jira: {exc}") from exc

    if resp.status_code == 404:
        raise JiraError(f"Ticket {key} not found (404). Check the key and the Jira URL.")
    if resp.status_code == 401:
        raise JiraError("Jira authentication failed (401). Check email and API token in Settings.")
    if resp.status_code != 200:
        raise JiraError(f"Jira returned HTTP {resp.status_code}.")

    data = resp.json()
    fields = data.get("fields", {})

    summary = fields.get("summary", "") or ""
    description = _flatten_description(fields.get("description") or "")
    acceptance_criteria = _extract_acceptance_criteria(fields)

    return {
        "key": key,
        "summary": summary.strip(),
        "description": description.strip(),
        "acceptance_criteria": acceptance_criteria.strip(),
    }


def _flatten_description(description) -> str:
    """Convert Jira ADF (or plain text) description to readable plain text."""
    if isinstance(description, str):
        return description

    parts = []

    def walk(node, depth=0):
        node_type = node.get("type")
        content = node.get("content", [])
        if node_type == "text":
            parts.append(node.get("text", ""))
        elif node_type in ("paragraph", "heading"):
            parts.append("\n")
            for child in content:
                walk(child, depth + 1)
            parts.append("\n")
        elif node_type == "listItem":
            prefix = "- " if depth % 2 == 0 else "  * "
            parts.append("\n" + prefix)
            for child in content:
                walk(child, depth + 1)
        elif node_type == "orderedList":
            for i, child in enumerate(content, start=1):
                parts.append(f"\n{i}. ")
                for sub in child.get("content", []):
                    walk(sub, depth + 1)
        elif node_type == "bulletList":
            for child in content:
                walk(child, depth + 1)
        elif node_type == "codeBlock":
            parts.append("\n```\n")
            for child in content:
                walk(child, depth + 1)
            parts.append("\n```\n")
        elif node_type in ("table", "tableRow", "tableCell", "tableHeader", "mediaGroup", "media", "applicationCard"):
            for child in content:
                walk(child, depth + 1)
        elif content:
            for child in content:
                walk(child, depth + 1)

    walk(description)
    text = "".join(parts)
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def _extract_acceptance_criteria(fields: dict) -> str:
    """Pull acceptance criteria from common custom field names, else from the description."""
    for key, value in fields.items():
        lowered = key.lower()
        if "acceptance" in lowered or "acceptancecriteria" in lowered.replace("_", ""):
            if isinstance(value, dict):  # ADF
                return _flatten_description(value)
            if isinstance(value, str):
                return value
    # Fallback: look for an "Acceptance Criteria" section in the description
    description = _flatten_description(fields.get("description") or "")
    marker = None
    for heading in ("Acceptance Criteria", "Acceptance criteria", "ACCEPTANCE CRITERIA"):
        idx = description.find(heading)
        if idx != -1:
            marker = heading
            break
    if marker:
        return description[idx + len(marker):].strip()
    return ""
