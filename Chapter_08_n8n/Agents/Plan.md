# Plan: 08 Screenshot to Bug Reporter

Design notes and model research for `08_Screenshot_To_Bug_Reporter_AIAgent.json`.

## The problem

Bug reporting is tedious and inconsistent. A tester sees a broken screen, grabs a
screenshot, then retypes every visual detail into a ticket by hand. The detail that
matters most (the red banner, the overlapping div, the truncated error string) is exactly
the part people summarise away.

```
Input:   UI screenshot + error logs
Output:  Jira bug with steps to reproduce, and the screenshot attached
```

## Decisions taken

| Question | Chosen | Why |
|---|---|---|
| Tracker | **Jira only** | Matches the implementation guide and reuses the `jiraSoftwareCloudApi` credential already in agents 01-05 |
| Model | **OpenRouter `minimax/minimax-m3:free`** | It is the free, multimodal option the reporter asked for. See the table below |
| Intake | **n8n Form Trigger** | Demos end to end with no separate front end; the form is the upload page |
| Screenshot | **Attached to the ticket** | The whole point is that the visual detail travels with the bug |
| Agent node | **Not used** | The model gets exactly one bounded job (look at the image, return JSON); every other step is a deterministic node. This is the agent-05 shape, not the agent-01 shape |

## Model research

Checked against the providers' live model lists, not from memory.

**Groq's vision lineup is down to a single model.** `llama-3.2-11b-vision-preview` is
gone, and Llama 4 Scout/Maverick no longer appear on the supported list. The only
image-capable model on Groq today is `qwen/qwen3.8-27b`, and it carries **Preview**
status (Groq's own note: evaluation only, may be discontinued at short notice). The
`qwen/qwen3.6-27b` id named in earlier drafts is stale — the served model is now 3.8.

| Provider | Model | $/M in | $/M out | Per report | Status |
|---|---|---|---|---|---|
| **OpenRouter (shipped)** | `minimax/minimax-m3:free` | 0 | 0 | **$0** | Free, rate limited |
| OpenRouter | `z-ai/glm-5.3-flash` | 0.035 | 0.50 | ~$0.0004 | Production |
| Groq | `qwen/qwen3.8-27b` | 0.80 | 4.00 | ~$0.005 | Preview |

Cost basis: the image costs a flat input charge (Groq bills 2048 tokens per image), plus
roughly 500 prompt tokens and roughly 700 output tokens. On Groq that is about 200 bug
reports per dollar; on GLM 5.3 Flash about 2,500; on the free endpoint, nothing but a
daily rate limit.

Both OpenRouter and Groq are OpenAI-compatible, so the request shape is identical
(`messages` array with a `text` part and an `image_url` part carrying a base64 data URL).
Only three fields differ:

| Field | OpenRouter | Groq |
|---|---|---|
| `url` | `https://openrouter.ai/api/v1/chat/completions` | `https://api.groq.com/openai/v1/chat/completions` |
| `nodeCredentialType` | `openRouterApi` | `groqApi` |
| `model` in `jsonBody` | `minimax/minimax-m3:free` | `qwen/qwen3.8-27b` |

The model id appears in exactly **one place** (the `jsonBody` of node 4), so swapping
providers is a one-field edit.

### Why the free endpoint is a real trade

`minimax/minimax-m3:free` is a multimodal model (text, image and video in; text out, 1M
context) served at zero cost. Two costs come with it:

1. **Rate limits.** Free endpoints are throttled (roughly 200 requests/day). Fine for a
   class demo, not for a team's daily bug intake.
2. **No per-key schema enforcement guarantee.** `response_format: {"type": "json_object"}`
   is sent, but free routing may not honour it every time. Node 5 therefore tolerates a
   fenced block or a non-JSON reply instead of trusting the shape. If you move to a paid
   OpenRouter model, `z-ai/glm-5.3-flash` is Production, and OpenRouter passes the
   `response_format` through; it still does not validate a schema server-side, so keep
   node 5's tolerance.

## Architecture

```
Form Trigger -> Normalize Intake -> Screenshot to Base64 -> OpenRouter Vision (HTTP)
                                                                    |
                       Jira: Create Bug <- Parse Bug Report <---------+
                               |
                       Prepare Attachment -> Jira: Add Attachment
```

This is **not** an AI Agent node. The model gets exactly one bounded job and every other
step is deterministic. An agent node would also make the image path harder to control,
since the tool-calling loop decides when and whether to look.

### Nodes

| # | Node | Type | Job |
|---|---|---|---|
| 1 | On bug report submission | `formTrigger` 2.2 | Hosted upload page: screenshot (required), error logs, steps, severity guess, environment |
| 2 | Normalize Intake | `code` 2 | Resolve the binary, build the system and user prompts |
| 3 | Screenshot to Base64 | `extractFromFile` 1.1 | Binary to a base64 string in `screenshot_b64` |
| 4 | OpenRouter Vision - Draft Bug Report | `httpRequest` 4.5 | One vision call, JSON mode, temperature 0.1 |
| 5 | Parse Bug Report | `code` 2 | Parse the response, render the Jira description, re-attach the binary |
| 6 | Jira - Create Bug | `jira` 1 | VWO project (10033), Bug type (10042) |
| 7 | Prepare Attachment | `code` 2 | Carry the issue key and the binary forward |
| 8 | Jira - Attach Screenshot | `jira` 1 | Resource `issueAttachment`, operation `add` |

Plus three sticky notes (Input / Action / Result).

### Four decisions worth knowing

**The binary property is resolved by position, not by name.** The Form Trigger names the
uploaded binary after the field label, and the exact form has changed between n8n
versions. Node 2 takes `Object.keys(item.binary)[0]` and re-keys it to a stable
`screenshot` property. Everything downstream depends on that name instead of on n8n's.

**The binary is re-attached twice.** Binary data does not survive the HTTP hop, and
Jira's create response carries none either. Node 5 pulls it back from
`$('Normalize Intake').first().binary`, and node 7 does the same, so the attachment step
still has the PNG.

**The prompts live in the Code node, not the HTTP node.** Multi-line strings render
readably in n8n's Code editor and become one unscrollable line inside an expression field.
The tradeoff is that the prompt sits one node upstream of the call that uses it.

**The Jira description is plain text, not wiki markup.** The Cloud API wraps a plain
string in a single ADF paragraph, so `h2.` and `{code}` would render literally. Node 5
builds the description line by line and joins with newlines.

### No secrets in this file

This workflow authenticates by reference, so there is nothing to redact:

```json
"authentication": "predefinedCredentialType",
"nodeCredentialType": "openRouterApi"
```

Nodes 6 and 8 reference the existing Jira credential (`jiraSoftwareCloudApi`,
"Jira SW Cloud account"). No API key appears anywhere in the exported JSON.

## Setup

1. Import via **Workflows > Import from File**.
2. Attach two credentials:
   - **OpenRouter** on node 4 (the free model needs an OpenRouter API key; a free key
     works). If the node shows no credential after import, open it and select one.
   - **Jira SW Cloud** on nodes 6 and 8.
3. Check node 3 shows the operation **Move File to Base64 String**. The internal key is
   `binaryToPropery`, a long-standing n8n typo. If the node loads blank, re-pick the
   operation from the dropdown.
4. Check node 8 (attach) shows resource **Issue Attachment** / operation **Add**. Re-pick
   from the dropdowns if it loaded blank.
5. Change the Jira project and issue type if you are not filing into VWO. Current values
   are project `10033` and issue type `10042`.
6. Activate, then open the form URL from the trigger node.

## Verification

Automated checks to run on the committed file:

- Valid JSON; every `connections` key and target resolves to a real node name
- Node ids unique and UUID4-shaped; all positions multiples of 16
- No embedded API key matches (`gsk_`, `sk-or-`, `Bearer`, `AIza`, `AQ.`)
- The chain is linear, 8 nodes, ending at the attachment step
- Every Code node parses under `node --check`

Manual runs, in this order:

1. **The negative case first.** Upload a screenshot of a perfectly healthy page. A good
   run returns `confidence: low` and an honest "no defect visible" summary. A bad run
   invents a defect to fill the schema. This is the run that tells you whether the system
   prompt's "do not invent" rules are actually holding, so it goes first after any prompt
   or model change.
2. **Happy path.** Upload a screenshot of a genuinely broken page plus a few log lines.
   Expect a VWO bug with numbered steps and the PNG attached and openable.
3. **Response shape.** Open node 4's output. `choices[0].message.content` should be bare
   JSON, not prose and not a fenced block. Node 5 strips one fence if it appears, but a
   fence every time means the prompt (or the model) needs attention.

## Known risks

- **The free endpoint is rate limited** and the model may not be pinned forever. The
  swap table above has the paid fallbacks.
- **No server-side schema enforcement.** The free routing may occasionally return prose;
  node 5 degrades gracefully (it files the ticket with a processing error rather than
  breaking the run).
- **Form binary naming** is the least certain part of the file, which is why node 2
  resolves it dynamically rather than hardcoding.
- **Text-heavy screenshots.** A dense screenshot costs the same as a sparse one but may
  exceed useful legibility. A downscale or crop step is a possible later addition.
