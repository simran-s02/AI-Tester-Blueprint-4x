# Screenshot to Bug Reporter - UI

A small web app for testers. Upload a screenshot of a bug; an AI workflow drafts the bug
report, creates the Jira issue, and attaches the image. The page then shows the new Jira
issue key with a link to it.

This folder is the custom front end for the n8n workflow:

```
../Agents/09_Screenshot_To_Bug_Reporter_AIAgent_UI.json
```

That is the **09** workflow. (Workflow `08_Screenshot_To_Bug_Reporter_AIAgent.json` is the
separate, form-only version that runs inside n8n - this UI does not use it.)

## How it works

```
browser --POST /api/report--> Vercel function --> n8n webhook (workflow 09)
(same origin, no CORS)        N8N_WEBHOOK_URL     vision -> Jira -> respond
```

- The browser never talks to n8n directly. The webhook URL stays server-side in the
  `N8N_WEBHOOK_URL` environment variable, so it is not exposed and no CORS setup is needed.
- The page posts the form (screenshot plus the text fields) as a `multipart/form-data`
  upload to `/api/report`.
- The serverless function streams that upload through to the n8n webhook untouched, then
  returns `{ issue_key, issue_url }` back to the page.

## Files

| File | Job |
|---|---|
| `index.html` | Vite page shell (loads `src/main.jsx`). |
| `src/main.jsx` | React entry point. |
| `src/App.jsx` | The whole UI: form, multipart POST to `/api/report`, show the result. |
| `src/App.css`, `src/index.css` | Styles. |
| `api/report.js` | Vercel function. Streams the multipart upload through to the n8n webhook. |
| `package.json` | Scripts and dependencies (React, Vite). |
| `vite.config.js`, `eslint.config.js` | Vite and ESLint config. |
| `.env`, `.env.example` | Local env (git-ignored) and its template. Holds `N8N_WEBHOOK_URL`. |

## Request and response

The page sends the form to `/api/report` as `multipart/form-data`:

| Field | Meaning |
|---|---|
| `screenshot` | The uploaded image file (required). |
| `error_logs` | Error logs (optional). |
| `steps_to_reproduce` | Steps to reproduce (optional). |
| `severity` | `S1`-`S4` (defaults to `S3`). |
| `environment` | Browser / OS / build (optional). |

The proxy forwards the same multipart body to the n8n webhook, so the screenshot arrives as
a normal binary file. Workflow 09 replies with `{ "issue_key": "...", "issue_url": "..." }`,
which the page renders.

## Setup

1. Import `../Agents/09_Screenshot_To_Bug_Reporter_AIAgent_UI.json` into n8n, attach the
   OpenRouter and Jira credentials, and **Activate** it. An inactive workflow's webhook
   returns 404.
2. In workflow 09, open the **Normalize Intake** node and set `JIRA_BASE_URL` to your Jira
   site (e.g. `https://your-domain.atlassian.net`). That is what the issue link is built from.
3. Copy `.env.example` to `.env` and set the **production** webhook URL (not the test one):

   ```
   N8N_WEBHOOK_URL=https://your-n8n-host/webhook/screenshot-bug-reporter
   ```

   The path segment is the one set on the "On UI submission" webhook node.

## Run locally

UI only (fast, but `/api/report` is not served this way):

```bash
npm install
npm run dev
```

Full end to end (UI plus the serverless function) - uses the Vercel CLI:

```bash
npm install
npx vercel dev
```

## Deploy

```bash
npx vercel
```

Set `N8N_WEBHOOK_URL` in the Vercel project environment (Production and Preview) and redeploy.

## Notes

- The n8n workflow is synchronous (one vision call plus two Jira hops). The proxy sets
  `maxDuration: 60`; on the Vercel Hobby plan the default limit is 10s, so this avoids a timeout.
- The proxy forwards the upload as `multipart/form-data`, so workflow 09's **Normalize
  Intake** node reads the screenshot as a binary file - no base64 conversion is involved.
