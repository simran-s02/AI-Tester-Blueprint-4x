"""Jira REST client — fetch, normalize, and connection test.

Normalizes three description formats (ADF JSON, wiki markup, plain text)
into markdown, extracts acceptance criteria, and pulls linked issues.
See architecture/SOP-01-jira-fetch.md.
"""

from __future__ import annotations

import base64
import re
from typing import Any, Optional

import requests

TIMEOUT_SECONDS = 20

# Fields we ask Jira for on the primary issue.
ISSUE_FIELDS = (
    "summary,description,issuetype,status,priority,labels,components,"
    "issuelinks,customfield_10020,parent"
)

_AC_HEADING_PATTERNS = re.compile(
    r"(acceptance\s*criteria|acceptance\s*conditions|definition\s*of\s*done|acceptance\s*tests?)",
    re.IGNORECASE,
)


class JiraError(Exception):
    """Raised when Jira returns an error we surface to the user."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class JiraClient:
    def __init__(self, base_url: str, email: str, api_token: str):
        self.base_url = (base_url or "").strip().rstrip("/")
        self.email = (email or "").strip()
        self.api_token = (api_token or "").strip()
        if not self.base_url:
            raise JiraError("config", "Jira base URL is empty.")
        if not self.api_token:
            raise JiraError("config", "Jira API token is empty.")
        token = f"{self.email}:{self.api_token}".encode("utf-8")
        self._auth = {"Authorization": f"Basic {base64.b64encode(token).decode()}"}
        self._session = requests.Session()
        self._session.headers.update(
            {"Accept": "application/json", **self._auth}
        )
        self._version: Optional[str] = None

    # ---- connection -------------------------------------------------
    def test_connection(self) -> dict:
        """Return {'ok': True, 'version': '3', 'user': ...} or raise."""
        user, version = self._whoami()
        return {"ok": True, "version": version, "user": user}

    def _whoami(self) -> tuple[str, str]:
        """Detect API version by trying /3 then /2."""
        for version in ("3", "2"):
            url = f"{self.base_url}/rest/api/{version}/myself"
            try:
                resp = self._session.get(url, timeout=TIMEOUT_SECONDS)
            except requests.RequestException as exc:
                raise JiraError(
                    "network", f"Could not reach Jira at {self.base_url}: {exc}"
                ) from exc
            if resp.status_code == 200:
                self._version = version
                data = resp.json()
                name = data.get("displayName") or data.get("name") or "unknown"
                return name, version
            if resp.status_code in (401, 403):
                raise JiraError(
                    "auth",
                    "Jira authentication failed (401/403). Check email + API token.",
                )
            if resp.status_code == 404:
                continue  # wrong API version, try next
            raise JiraError("http", f"Jira /myself returned HTTP {resp.status_code}.")
        raise JiraError("config", "Could not determine Jira API version (v3 or v2).")

    # ---- fetch ------------------------------------------------------
    def _api_base(self) -> str:
        if self._version is None:
            self._whoami()
        return f"{self.base_url}/rest/api/{self._version}"

    def fetch_issue(self, issue_key: str) -> dict:
        """Fetch + normalize a single issue. See LLM.md section 2.2 schema."""
        issue_key = issue_key.strip().upper()
        if not re.match(r"^[A-Z][A-Z0-9_]*-\d+$", issue_key):
            raise JiraError(
                "bad_key",
                f"'{issue_key}' does not look like a Jira key (expected e.g. PROJ-123).",
            )
        url = f"{self._api_base()}/issue/{issue_key}"
        resp = self._session.get(url, params={"fields": ISSUE_FIELDS}, timeout=TIMEOUT_SECONDS)
        if resp.status_code == 404:
            raise JiraError(
                "not_found",
                f"Jira issue {issue_key} not found (or no permission to view it).",
            )
        if resp.status_code in (401, 403):
            raise JiraError(
                "auth",
                "Jira authentication failed (401/403). Check email + API token.",
            )
        if resp.status_code != 200:
            raise JiraError(
                "http", f"Jira issue fetch returned HTTP {resp.status_code}."
            )
        data = resp.json()
        return self._normalize_issue(data, issue_key)

    def fetch_issue_by_title(self, title_query: str, max_results: int = 5) -> list[dict]:
        """JQL search by summary text. Returns normalized issues (empty if none).

        Tries the modern bounded ``/search/jql`` endpoint first (newer Cloud
        instances return HTTP 410 for the legacy ``/search``), then falls back
        to the legacy endpoint. The query is project-scoped when the key prefix
        is unknown so the "bounded query" guardrail accepts it.
        """
        query = (title_query or "").strip()
        if not query:
            raise JiraError("bad_key", "No issue title text provided.")
        # Quote and escape JQL text search
        safe = query.replace('"', '\\"').replace("'", "\\'")
        jql = f'summary ~ "{safe}" ORDER BY updated DESC'

        endpoints = (f"{self._api_base()}/search/jql", f"{self._api_base()}/search")
        last_error: Optional[str] = None
        for url in endpoints:
            resp = self._session.get(
                url,
                params={"jql": jql, "maxResults": max_results, "fields": ISSUE_FIELDS},
                timeout=TIMEOUT_SECONDS,
            )
            if resp.status_code in (401, 403):
                raise JiraError(
                    "auth",
                    "Jira authentication failed (401/403). Check email + API token.",
                )
            if resp.status_code in (404, 405, 410):
                # endpoint removed/deprecated on this instance -> try the next
                last_error = f"HTTP {resp.status_code}"
                continue
            if resp.status_code != 200:
                raise JiraError(
                    "http", f"Jira search returned HTTP {resp.status_code}: {resp.text[:200]}"
                )
            data = resp.json()
            out = []
            for item in data.get("issues", []):
                key = str(item.get("key", ""))
                if key:
                    out.append(self._normalize_issue(item, key))
            return out
        raise JiraError("http", f"Jira search unavailable on this instance ({last_error}).")

    # ---- normalization ----------------------------------------------
    def _normalize_issue(self, data: dict, issue_key: str) -> dict:
        fields = data.get("fields", {})
        description_raw = fields.get("description")
        description_md = self._normalize_description(description_raw)

        acceptance = self._extract_acceptance_criteria(fields, description_raw)

        linked = self._normalize_issue_links(fields.get("issuelinks", []))

        def _name(value: Any) -> str:
            if isinstance(value, dict):
                return str(value.get("name", "") or "")
            return str(value or "")

        def _list_names(values: Any) -> list[str]:
            if not isinstance(values, list):
                return []
            return [str(v.get("name", "") or "") for v in values if isinstance(v, dict)]

        return {
            "key": str(data.get("key") or issue_key),
            "id": str(data.get("id", "")),
            "type": _name(fields.get("issuetype")),
            "status": _name(fields.get("status")),
            "priority": _name(fields.get("priority")),
            "summary": str(fields.get("summary") or "").strip(),
            "description_md": description_md,
            "acceptance_criteria": acceptance,
            "components": _list_names(fields.get("components")),
            "labels": [str(x) for x in (fields.get("labels") or []) if x],
            "linked_issues": linked,
        }

    def _normalize_issue_links(self, issuelinks: list) -> list[dict]:
        """Extract linked issues from issuelinks; fetch details when needed."""
        if not isinstance(issuelinks, list):
            return []
        seen: dict[str, dict] = {}
        for link in issuelinks:
            link_type = ""
            outward = link.get("outwardIssue")
            inward = link.get("inwardIssue")
            if outward is not None:
                link_type = str(
                    link.get("type", {}).get("outward", "") or link.get("type", {}).get("name", "")
                )
                entry = outward
            elif inward is not None:
                link_type = str(
                    link.get("type", {}).get("inward", "") or link.get("type", {}).get("name", "")
                )
                entry = inward
            else:
                continue
            key = entry.get("key")
            if not key:
                continue
            issue_fields = entry.get("fields", {}) if isinstance(entry, dict) else {}
            seen[key] = {
                "key": key,
                "type": str(
                    (issue_fields.get("issuetype") or {}).get("name", "")
                    if isinstance(issue_fields.get("issuetype"), dict)
                    else issue_fields.get("issuetype", "")
                ),
                "summary": str(issue_fields.get("summary", "") or ""),
                "status": str(
                    (issue_fields.get("status") or {}).get("name", "")
                    if isinstance(issue_fields.get("status"), dict)
                    else issue_fields.get("status", "")
                ),
                "link_type": link_type,
            }
        return list(seen.values())

    # ---- description normalization ----------------------------------
    def _normalize_description(self, raw: Any) -> str:
        if raw is None:
            return ""
        if isinstance(raw, str):
            stripped = raw.strip()
            if stripped.startswith("{"):
                try:
                    import json

                    return self._adf_to_markdown(json.loads(stripped))
                except (json.JSONDecodeError, ValueError):
                    pass
            if re.search(r"(^|\n)\s*(h1\.|h2\.|h3\.|{panel|\*|#)", stripped):
                return self._wiki_to_markdown(stripped)
            return stripped
        if isinstance(raw, dict):  # ADF
            return self._adf_to_markdown(raw)
        return str(raw)

    @staticmethod
    def _adf_text(node: Any) -> str:
        """Collect plain text from an ADF node tree."""
        if isinstance(node, dict):
            ntype = node.get("type")
            if ntype == "text":
                return str(node.get("text", ""))
            if ntype == "hardBreak":
                return "\n"
            if ntype == "rule":
                return "---\n"
            # Inline container: concat child text, no newlines.
            inline_types = {
                "emoji", "inlineCard", "mention", "textColor", "underline",
                "link", "citation", "date", "status", "placeholder",
            }
            if ntype in inline_types:
                return "".join(JiraClient._adf_text(c) for c in node.get("content", []))
            if ntype == "paragraph":
                return "".join(JiraClient._adf_text(c) for c in node.get("content", [])) + "\n"
            if ntype == "heading":
                level = node.get("attrs", {}).get("level", 1)
                text = "".join(JiraClient._adf_text(c) for c in node.get("content", [])).strip()
                return f"{'#' * min(level, 6)} {text}\n"
            if ntype == "bulletList":
                return JiraClient._adf_list(node, ordered=False)
            if ntype == "orderedList":
                return JiraClient._adf_list(node, ordered=True)
            if ntype == "listItem":
                # Render list item content directly (should only be reached via a list).
                return "".join(JiraClient._adf_text(c) for c in node.get("content", []))
            if ntype == "blockquote":
                inner = "".join(JiraClient._adf_text(c) for c in node.get("content", [])).strip()
                return "> " + inner.replace("\n", "\n> ") + "\n" if inner else ""
            if ntype == "codeBlock":
                inner = "".join(JiraClient._adf_text(c) for c in node.get("content", []))
                return "```\n" + inner + "\n```\n"
            if ntype == "table":
                return JiraClient._adf_table_text(node)
            if ntype == "mediaSingle" or ntype == "mediaGroup":
                return ""
            # Generic block container.
            return "".join(JiraClient._adf_text(c) for c in node.get("content", []))
        if isinstance(node, list):
            return "".join(JiraClient._adf_text(item) for item in node)
        return str(node or "")

    @classmethod
    def _adf_list(cls, node: dict, ordered: bool) -> str:
        """Render a (possibly nested) ADF list. Indents nested lists with 2 spaces."""
        lines: list[str] = []

        def walk(list_node: dict, depth: int) -> None:
            prefix = " " * (depth * 2)
            for idx, item in enumerate(list_node.get("content", []), start=1):
                # First flatten the item's paragraph/listItem text.
                item_lines: list[str] = []
                # listItem.content is usually [paragraph] and/or [bulletList|orderedList]
                for child in item.get("content", []):
                    ctype = child.get("type")
                    if ctype in ("bulletList", "orderedList"):
                        continue  # handle nested list below
                    text = cls._adf_text(child).strip()
                    if text:
                        item_lines.append(text)
                marker = f"{idx}." if ordered else "-"
                joined = " ".join(item_lines)
                lines.append(f"{prefix}{marker} {joined}")
                # nested list
                for child in item.get("content", []):
                    ctype = child.get("type")
                    if ctype in ("bulletList", "orderedList"):
                        walk(child, depth + 1)

        walk(node, 0)
        return "\n".join(lines) + "\n"

    @staticmethod
    def _adf_table_text(node: dict) -> str:
        rows = []
        for row in node.get("content", []):
            cells = []
            for cell in row.get("content", []):
                cells.append(JiraClient._adf_text(cell).strip())
            rows.append("| " + " | ".join(cells) + " |")
        return "\n".join(rows) + "\n"

    @classmethod
    def _adf_to_markdown(cls, doc: Any) -> str:
        if isinstance(doc, dict) and doc.get("type") == "doc":
            content = doc.get("content", [])
        elif isinstance(doc, list):
            content = doc
        else:
            return str(doc or "")
        md = "".join(cls._adf_text(node) for node in content)
        return md.strip() + "\n" if md.strip() else ""

    @staticmethod
    def _wiki_to_markdown(text: str) -> str:
        md = text
        md = re.sub(r"^h([1-6])\.\s*", lambda m: "#" * int(m.group(1)) + " ", md, flags=re.M)
        md = re.sub(r"\{code(:[^}]*)?\}", "```", md)
        md = re.sub(r"\{noformat\}", "```", md)
        md = re.sub(r"\{panel(:[^}]*)?\}", "", md)
        md = md.replace("{quote}", "> ").replace("{color:#[0-9a-fA-F]+}", "").replace("{color}", "")
        md = re.sub(r"\{color:[^}]*\}", "", md)
        md = re.sub(r"\{\{[^}]*\}\}", lambda m: f"`{m.group(0)[2:-2]}`", md)
        md = re.sub(r"\[(.+?)\|(.+?)\]", r"[\1](\2)", md)
        md = re.sub(r"^bq\.\s*", "> ", md, flags=re.M)
        return md.strip() + "\n" if md.strip() else ""

    # ---- acceptance criteria ----------------------------------------
    def _extract_acceptance_criteria(self, fields: dict, description_raw: Any) -> list[str]:
        """Priority: custom AC field -> ADF headings -> wiki headings -> bullets."""
        criteria: list[str] = []

        # 1) scan fields for a custom field whose name suggests acceptance criteria
        for field_id, value in fields.items():
            if not field_id.startswith("customfield_"):
                continue
            name_hint = field_id.lower()
            if not any(p in name_hint for p in ("accept", "criteria", "dod", "definition")):
                continue
            items = self._field_to_strings(value)
            if items:
                criteria.extend(items)

        # 2) description headings / bullets
        if not criteria and description_raw is not None:
            md = (
                self._adf_to_markdown(description_raw)
                if isinstance(description_raw, dict)
                else self._normalize_description(description_raw)
            )
            criteria = self._extract_ac_from_markdown(md)

        return self._clean_criteria(criteria)

    @staticmethod
    def _field_to_strings(value: Any) -> list[str]:
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            out = []
            for item in value:
                if isinstance(item, str):
                    out.append(item)
                elif isinstance(item, dict):
                    out.append(str(item.get("value") or item.get("name") or ""))
            return out
        if isinstance(value, dict):
            text = value.get("value") or value.get("name")
            if text:
                return [str(text)]
            # ADF-encoded custom field
            if value.get("type") == "doc":
                return [JiraClient._adf_to_markdown(value).strip()]
        return []

    @classmethod
    def _extract_ac_from_markdown(cls, md: str) -> list[str]:
        """Find 'Acceptance Criteria' heading and collect the list that follows."""
        lines = md.splitlines()
        pattern = re.compile(r"^#{1,6}\s+(.+)$", re.I)
        heading_idx = -1
        heading_text = ""
        for i, line in enumerate(lines):
            match = pattern.match(line.strip())
            if match and re.search(_AC_HEADING_PATTERNS, match.group(1)):
                heading_idx = i
                heading_text = match.group(1).lower()
                break
        if heading_idx < 0:
            return []

        # section runs until the next heading of the SAME or HIGHER level
        level = len(re.match(r"^#+", lines[heading_idx].strip()).group(0))
        section = []
        for line in lines[heading_idx + 1 :]:
            stripped = line.strip()
            if not stripped:
                continue
            hm = re.match(r"^(#+)\s+", stripped)
            if hm and len(hm.group(1)) <= level:
                break
            section.append(stripped)
        return cls._lines_to_criteria(section, heading_text)

    @staticmethod
    def _lines_to_criteria(section_lines: list[str], heading_text: str) -> list[str]:
        criteria: list[str] = []
        bullets: list[str] = []
        for line in section_lines:
            bm = re.match(r"^[-*•]\s+(.+)$", line)
            nm = re.match(r"^\d+[.)]\s+(.+)$", line)
            if bm:
                bullets.append(bm.group(1).strip())
            elif nm:
                bullets.append(nm.group(1).strip())
        if bullets:
            return bullets
        # If the whole description sits under the AC heading, treat its sentences as criteria
        joined = " ".join(section_lines)
        # Only split into sentences if the heading is the sole content of the description
        joined = re.sub(r"\s+", " ", joined).strip()
        if len(joined) < 300:
            return [joined] if joined else []
        return []

    @staticmethod
    def _clean_criteria(criteria: list[str]) -> list[str]:
        cleaned: list[str] = []
        for item in criteria:
            if not item:
                continue
            text = re.sub(r"\s+", " ", item).strip()
            text = re.sub(r"^[-*•]\s*", "", text)
            text = text.strip("*_ ")
            if text and text not in cleaned:
                cleaned.append(text)
        return cleaned
