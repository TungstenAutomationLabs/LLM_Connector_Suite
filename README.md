# LLM Connector Suite
### For Tungsten TotalAgility 2026.1

[![TotalAgility](https://img.shields.io/badge/TotalAgility-2026.1-blue)](https://www.tungsten.com)
[![Version](https://img.shields.io/badge/Version-1.0-brightgreen)]()

> A suite of production-ready AI connectors for Tungsten TotalAgility, enabling text, document, and image processing through a consistent interface across leading AI models.

---

## What Is This?

Stop rebuilding AI integrations every time a new model ships. The LLM Connector Suite provides a consistent interface for integrating AI capabilities into Tungsten TotalAgility workflows.

The LLM Connector Suite enables Tungsten TotalAgility processes and third-party applications to interact with leading AI models through a standardized interface. 
Each connector follows the same input, output, and routing pattern, allowing organizations to switch AI providers with minimal workflow changes.

---

## Connector Overview

| Connector | AI Provider | Platform | Status |
|---|---|---|---|
| Claude | Anthropic | Azure AI Foundry | Available |
| Nova | Amazon | AWS Bedrock | Available |
| Gemini | Google | Google AI Studio | Available |
| Gemma | Google | Google Vertex AI | Coming Soon |


---

## Supported Input Types
| Input | Claude | Nova | Gemini | Gemma |
|---|---|---|---|---|
| Plain text | ✅ | ✅ | ✅ | 🔄 Soon |
| PDF document | ✅ | ✅ | ✅ | 🔄 Soon |
| Image (JPG, PNG, TIFF) | ✅ | ✅ | ✅ | 🔄 Soon |
| Pre-encoded base64 | ✅ | ✅ | ✅ | 🔄 Soon |
| Document + Image combo | ✅ | ✅ | ✅ | 🔄 Soon |
| DOCX, BMP | ❌ | ❌ | ❌ | ❌ |

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


<img width="502" height="490" alt="image" src="https://github.com/user-attachments/assets/1f0e8db3-20c8-4f38-8953-44e90020df8a" />

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

1. Download the LLM_Connector_Suite.zip from its folder
2. TA Designer → Import → browse to .zip → Import
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
| Model | String | Optional | Override the model ID |
| max_token | Long | Optional | Token limit (default 500) |
| temperature | Short | Optional | Randomness (default 0.5) |


**NOTE:** System prompts are configured through the LLM_Connector_Suite Custom Service Group and are not exposed as process input variables. Each connector uses its own server variable for system prompt configuration (for example: Claude_System_Prompt, Nova_System_Prompt, Gemini_System_Prompt).

Model selection behavior varies by connector. Claude and Nova support model configuration through the Model variable, while Gemini uses the configured endpoint and provider defaults.
### Outputs

| Variable | Type | Description |
|---|---|---|
| LLM_RESPONSE | String | Response returned by the AI model |
| STATUS | String | Success or error status |
| LLM_TOKENS | String | Total tokens consumed for the request |


---

## Input Scenarios (all connectors)

| Scenario | QUESTION | HAS_DOCORIMAGE | HAS_DOCANDIMAGE | DOCBASE64 | IMAGEBASE64 | File Upload |
|---|---|---|---|---|---|---|
| Text only | Yes | false | false | - | - | - |
| Single file (PDF/image) | Yes | true | false | - | - | one file |
| Combo (doc + image) | Yes | true | true | - | - | two files |
| Third-party single | Yes | false | false | yes | - | - |
| Third-party combo | Yes | false | false | yes | yes | - |

> For third-party combo, both flags stay false

## How to Test (TA Debug)

<img width="672" height="398" alt="image" src="https://github.com/user-attachments/assets/1caaf744-4241-4311-a013-324421aea2f6" />



> Key rule: Document field = any single file. Image File field = the second file for combo only.

---

## Default System Prompt

To ensure consistent responses across supported AI providers, each connector uses a predefined system prompt. The default prompt is shown below and can be customized through the connector-specific system prompt server variable.


You are an intelligent assistant integrated into a Tungsten TotalAgility workflow.\n\nRules:\n- If a document or image is provided, base your response strictly on its content.\n- If only a text question is provided, answer from general knowledge accurately and concisely.\n- If asked to extract structured data, return valid JSON only — no markdown, no preamble, no explanation.\n- If the input is unclear or insufficient to answer, say so explicitly rather than guessing.\n- Keep responses professional and factual.\n- Do not make up information not present in provided content (when content is given).

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
