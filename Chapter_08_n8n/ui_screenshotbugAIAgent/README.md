# Screenshot to Bug Reporter — UI

The custom front end for workflow `../Agents/09_Screenshot_To_Bug_Reporter_AIAgent_UI.json`.
A tester uploads a screenshot, the workflow drafts the bug, files it in Jira, attaches the
image, and this page shows the new issue key.

```
browser ──POST /api/report──▶ Vercel function ──▶ n8n webhook (09)
(same origin, no CORS)         N8N_WEBHOOK_URL     vision → Jira → respond
```

The browser never talks to n8n directly: the webhook URL stays server-side (`N8N_WEBHOOK_URL`),
so it is not exposed to the page and no CORS setup is needed.

## Files

| File | Job |
|---|---|
| `index.html` | The upload form. Posts `multipart/form-data` to `/api/report`. |
| `api/report.js` | Serverless proxy. Streams the upload through to the n8n webhook untouched. |
| `.env.example` | Copy to `.env` and set `N8N_WEBHOOK_URL`. |

## Setup

1. Import the 09 workflow, attach the OpenRouter and Jira credentials, and **Activate** it.
   An inactive workflow's webhook returns 404.
2. In `09_…_UI.json`, open **Normalize Intake** and set `JIRA_BASE_URL` at the top to your
   Jira site (e.g. `https://your-domain.atlassian.net`). That is what the page's issue link
   is built from.
3. Copy `.env.example` to `.env` and set `N8N_WEBHOOK_URL`. Use the **production** webhook
   (`/webhook/<path>`), not the test one (`/webhook-test/<path>`):

   ```
   N8N_WEBHOOK_URL=https://your-n8n-host/webhook/screenshot-bug-reporter
   ```

   The path segment is the one set on the `On UI submission` node.

## Run locally

```bash
npx vercel dev
```

Then open the URL it prints and submit a screenshot.

## Deploy

```bash
npx vercel
```

Set `N8N_WEBHOOK_URL` as an environment variable in the Vercel project (Production and
Preview), then redeploy. No build step and no dependencies are required.

## Notes

- The proxy sets `maxDuration: 60`. The workflow is synchronous — one vision call plus two
  Jira hops — which can exceed Vercel's 10s default on the Hobby plan.
- The screenshot arrives at n8n as a normal multipart upload, so the workflow's binary
  handling matches the form-based 08 workflow.
