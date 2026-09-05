# SOP-01 — Jira Fetch & Normalize

**Layer:** 3 (Tools) · **Module:** `tools/jira_client.py` · **Status:** Implemented

## Goal
Given a Jira issue key (e.g. `PROJ-123`), authenticate to a user's Jira instance and return a **normalized** issue dict (markdown description + extracted acceptance criteria + linked issues). Never returns raw ADF to the rest of the pipeline.

## Input
- `base_url`, `email`, `api_token` (from settings)
- `issue_key`

## Behavior
1. Build Basic Auth header: `base64(email:api_token)`.
2. **Version detection:** try `GET {base}/rest/api/3/myself`; if 404, retry `GET {base}/rest/api/2/myself`. Store detected version.
3. **Fetch issue:** `GET {base}/rest/api/{v}/issue/{key}?fields=...` requesting only needed fields.
4. **Normalize description:** ADF JSON → markdown; wiki markup `{panel}`/`h1.` → markdown; plain text passthrough.
5. **Extract acceptance criteria:** priority order:
   a. a custom field whose name/id contains "acceptance" (scan `expand`/creatable meta when possible, else known candidates from the response fields);
   b. ADF/description blocks under a heading containing "acceptance criteria";
   c. wiki-markup sections under `h2. Acceptance Criteria`;
   d. bullet list items in the description.
6. **Linked issues:** read `fields.issuelinks`, collect outward/inward keys + summaries; batch-fetch via JQL `key in (...)`, `fields=summary,status,issuetype`.
7. **Title search (by-title lookup):** newer Jira instances deprecate `GET /rest/api/3/search`
   (HTTP 410) and require the bounded `GET /rest/api/3/search/jql`. The client therefore:
   - builds `summary ~ "<query>" AND project in (<projects>) ORDER BY updated DESC` (bounded so the JQL guardrail accepts it);
   - tries `/search/jql` first, then falls back to the legacy `/search` on 404/410/405.
8. Return normalized dict (schema in `LLM.md` §2.2).

## Edge Cases
- 401/403 → raise `JiraError("auth")` (UI: "check email/token").
- 404 on issue → `JiraError("not_found")`.
- No acceptance criteria found → empty list (downstream flags a gap).
- Custom field scan misses the AC field → description-heading heuristic is the fallback.
- Empty description → `description_md=""`.

## Golden Rule
If fetch/normalize logic changes, update this SOP first, then the code.
