# LLM Connector Suite
### For Tungsten TotalAgility 2026.1

[![TotalAgility](https://img.shields.io/badge/TotalAgility-2026.1-blue)](https://www.tungsten.com)
[![Version](https://img.shields.io/badge/Version-1.0-brightgreen)]()

> A suite of plug-and-play AI connectors for Tungsten TotalAgility. Send text, documents, and images to leading AI models — no API knowledge required.

---

## What Is This?

The LLM Connector Suite lets any TotalAgility process or third-party system call multiple AI models through a unified interface. Developers drop a connector into their workflow, map variables, and get an AI response — without knowing the underlying API.

Every connector follows the same structure: same input variables, same output variables, same routing logic. Only the backend (Azure, AWS, Google) differs.

---

## Connector Overview

| Connector | Model | Provider | Cloud | Status |
|---|---|---|---|---|
| Claude | claude-opus-4-6 | Anthropic | Azure AI Foundry | v1.0 |
| Nova | amazon.nova-lite-v1 | Amazon | AWS Bedrock | v1.0 |
| Gemini | gemini-pro | Google | Google AI Studio | Coming v1.1 |
| Gemma | gemma-2 | Google | Google Vertex AI | Coming v1.2 |

---

## Repository Structure

```
LLM_Connector_Suite/
|
├── Claude/
│   ├── LLMConnector_Claude_v1.0.zip
│   ├── README.md
│   └── TestCases.xlsx
|
├── Nova/
│   ├── LLMConnector_Nova_v1.0.zip
│   ├── lambda_function.py
│   ├── README.md
│   └── TestCases.xlsx
|
├── Gemini/
│   └── coming-soon.md
|
├── Gemma/
│   └── coming-soon.md
|
└── README.md   (this file)
```

---

## Supported Input Types

| Input | Claude | Nova | Gemini | Gemma |
|---|---|---|---|---|
| Plain text | Yes | Yes | Soon | Soon |
| PDF document | Yes | Yes | Soon | Soon |
| Image (JPG, PNG, GIF, WebP) | Yes | Yes | Soon | Soon |
| Pre-encoded base64 | Yes | Yes | Soon | Soon |
| Document + Image combo | Yes | Yes | Soon | Soon |
| DOCX, BMP | No | No | No | No |

---

## How It Works

```
TA Process / Third-Party System
           |
           v
   LLM Connector (TA process)
   1. Detect input type (text / doc / image / combo)
   2. Convert file to base64 (if uploaded in TA)
   3. Call the AI model
   4. Parse response + tokens
   5. Return answer
           |
           v
   RESPONSE + STATUS + TOKEN COUNTS
```

**Routing logic (same for all connectors):**

```
Start
 → Document present? script   (sets DOCEXISTS, IMAGEEXISTS)
 → DOCEXISTS?
     False → [Model]-text → Capture → End
     True  → Has both image and document?  (IMAGEEXISTS = true)
                 True  → [convert if needed] → [Model]-Combo → Capture → End
                 False → Base64 present?
                             True  → [Model]-doc/image → Capture → End
                             False → Convert to Base64 → [Model]-doc/image → Capture → End
```

---

## Prerequisites (all connectors)

| Requirement | Detail |
|---|---|
| TotalAgility | 2026.1+ |
| LLM Connectors category | Create in TA Designer |
| KTA_SERVICE_URI server variable | Set to your TA SDK base URL |
| Model backend | Azure / AWS / Google account per connector |

---

## Installation (any connector)

1. Download the connector .zip from its folder
2. TA Designer → Admin → Import → browse to .zip → Import
3. Set required server variables (see connector README)
4. Test using TA Debug

---

## Common Variables (all connectors)

### Inputs

| Variable | Type | Required | Description |
|---|---|---|---|
| QUESTION | String | Always | Your prompt or question |
| HAS_DOCORIMAGE | Bool | Uploading one file in TA | Tick when uploading a single file (PDF or image) |
| HAS_DOCANDIMAGE | Bool | Combo upload in TA | Tick when uploading two files (doc + image) |
| DOCBASE64 | String | Third-party | Pre-encoded base64 of the main file |
| IMAGEBASE64 | String | Third-party combo | Pre-encoded base64 of the second file |
| SYSTEMPROMPT | String | Optional | Overrides default system prompt |
| Model | String | Optional | Override the model ID |
| max_token | Long | Optional | Token limit (default 500) |
| temperature | Short | Optional | Randomness (default 0.5) |

### Outputs

| Variable | Type | Description |
|---|---|---|
| RESPONSE | String | The AI answer |
| STATUS | String | OK or error message |
| INPUT_TOKENS | String | Tokens sent |
| OUTPUT_TOKENS | String | Tokens returned |

> Output naming differs slightly per connector: CLAUDE_RESPONSE, NOVA_RESPONSE, etc.

---

## Input Scenarios (all connectors)

| Scenario | QUESTION | HAS_DOCORIMAGE | HAS_DOCANDIMAGE | DOCBASE64 | IMAGEBASE64 | File Upload |
|---|---|---|---|---|---|---|
| Text only | Yes | false | false | - | - | - |
| Single file (PDF/image) | Yes | true | false | - | - | one file |
| Combo (doc + image) | Yes | true | true | - | - | two files |
| Third-party single | Yes | false | false | yes | - | - |
| Third-party combo | Yes | false | false | yes | yes | - |

> For third-party combo, both flags stay false — IMAGEEXISTS is set automatically because IMAGEBASE64 is present.

---

## How to Test (TA Debug)

```
+------------------+----------------------------------------------+
| Scenario         | What to fill                                 |
+------------------+----------------------------------------------+
| Text only        | QUESTION only                                |
|                  | HAS_DOCORIMAGE  = unchecked                   |
|                  | HAS_DOCANDIMAGE = unchecked                   |
+------------------+----------------------------------------------+
| Single file      | QUESTION                                     |
| (PDF or image)   | Document       = Browse -> upload your file   |
|                  | HAS_DOCORIMAGE  = TICK                        |
|                  | HAS_DOCANDIMAGE = unchecked                   |
+------------------+----------------------------------------------+
| Combo            | QUESTION                                     |
| (two files)      | Document       = Browse -> first file         |
|                  | Image File     = Browse -> second file        |
|                  | HAS_DOCORIMAGE  = TICK                        |
|                  | HAS_DOCANDIMAGE = TICK                        |
+------------------+----------------------------------------------+
| Third party      | Send base64 in request body                  |
| (API)            | both flags unchecked                         |
+------------------+----------------------------------------------+
```

> Key rule: Document field = any single file. Image File field = the second file for combo only.

### Recommended test order

| # | Scenario | Key check |
|---|---|---|
| 1 | Text only | RESPONSE returns answer |
| 2 | PDF upload | RESPONSE describes PDF |
| 3 | JPG upload | RESPONSE describes image |
| 4 | Combo doc + image | RESPONSE compares both |
| 5 | Third-party base64 | RESPONSE via API |
| 6 | Empty question | STATUS = question cannot be empty |
| 7 | File without ticking flag | File ignored, text path only |

---

## Default System Prompt

All connectors use this default (configurable via server variable):

```
You are an intelligent assistant integrated into a Tungsten TotalAgility workflow.

Rules:
- If a document or image is provided, base your response strictly on its content.
- If only a text question is provided, answer from general knowledge accurately and concisely.
- If asked to extract structured data, return valid JSON only — no markdown, no preamble, no explanation.
- If the input is unclear or insufficient to answer, say so explicitly rather than guessing.
- Keep responses professional and factual.
- Do not make up information not present in provided content (when content is given).
```

---

## Connector-Specific Setup

### Claude
- Requires Azure AI Foundry account + Claude model deployed
- Server variables: Claude_API_Key, Claude_System_Prompt
- Calls Azure endpoint directly via RESTful activity
- See Claude/README.md

### Nova
- Requires AWS account + Bedrock access + API Gateway + Lambda
- Server variables: Nova_API_Key, Nova_System_Prompt
- Calls API Gateway which triggers Lambda which calls Bedrock
- See Nova/README.md

### Gemini (coming v1.1)
- Requires Google AI Studio account + API key
- Server variables: Gemini_API_Key, Gemini_Endpoint_URL

### Gemma (coming v1.2)
- Requires Google Cloud Vertex AI + Gemma model deployed
- Server variables: Gemma_API_Key, Gemma_Endpoint_URL

---

## Security

| Rule | Detail |
|---|---|
| API keys in server variables | Never hardcoded in processes or scripts |
| Server variables not exported | Keys stay in your environment, not in the zip |
| Keys not in GitHub | .gitignore excludes config files |
| Never hardcode keys | Do not put API keys in process variables or scripts |

---

## Do's and Don'ts

### Do
- Store all API keys in server variables only
- Set HAS_DOCORIMAGE = true when uploading a single file in TA debug
- Set both flags when uploading a combo (doc + image)
- Check STATUS = OK before using the response downstream
- Use SYSTEMPROMPT to control output format per use case
- Ask for JSON in your prompt if you need structured data

### Don't
- Don't send DOCX or BMP files — not supported by any connector
- Don't expect conversation memory — each call is stateless
- Don't hardcode API keys anywhere

---

## Error Reference

| Error | Cause | Fix |
|---|---|---|
| Question cannot be empty | QUESTION not set | Set QUESTION before calling |
| DOCEXISTS false despite upload | Flag not ticked | Tick HAS_DOCORIMAGE in debug |
| An error occurred: HTTP | Convert to Base64 failed | Check KTA_SERVICE_URI server variable |
| STATUS = error | API key wrong or expired | Check API key server variable |
| Job suspended / Index error | Variable type mismatch | temperature = Short, max_token = Long |
| File too large | Base64 over limit | Reduce file size |
| ValidationException | File name or format issue | Lambda auto-handles MIME and filename |

---

## Versioning

| Version | Changes |
|---|---|
| v1.0 | Claude + Nova — text, doc, image, combo |
| v1.1 | Gemini connector + Custom Service packaging |
| v1.2 | Gemma connector |
| v1.3 | DOCX pre-conversion, URL-based document source |

---

## Roadmap

- Convert to Custom Service (v1.1)
- Add CONTENT_LENGTH_BYTES early-rejection check
- Gemini connector (Google AI Studio)
- Gemma connector (Google Vertex AI)
- DOCX to PDF pre-conversion
- URL-based document source support

---

## Built By

Tungsten Automation Centre of Excellence (CoE)
Platform: Tungsten TotalAgility 2026.1

Claude - Azure AI Foundry | Nova - AWS Bedrock | Gemini - Google AI Studio | Gemma - Google Vertex AI
