# CBE PoC — Iso-Production Test Harness

## What This Does

Simulates a **production-like AI support agent** (MedSecure Technologies) with:

- **System prompt** containing confidential configuration (API keys, DB creds, endpoints)
- **Knowledge base** (4 documents) simulating Azure AI Search with internal docs
- **4 tools** simulating real integrations (search, patient lookup, ticketing, prescriptions)
- **10 CBE payloads** + 2 baselines testing various attack vectors
- **Automatic secret detection** against 25+ known secrets

## Quick Start

### Option 1: OpenAI API

```bash
npm install openai
OPENAI_API_KEY=sk-xxx node run-poc.js
```

### Option 2: Azure OpenAI

```bash
npm install openai
AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com \
AZURE_OPENAI_KEY=xxx \
AZURE_OPENAI_DEPLOYMENT=gpt-4o \
node run-poc.js
```

### Option 3: Anthropic (Claude)

```bash
npm install @anthropic-ai/sdk
ANTHROPIC_API_KEY=sk-ant-xxx node run-poc.js --provider anthropic
```

## Options

```
--provider openai|azure|anthropic   Provider to use (auto-detected from env)
--model MODEL_NAME                  Override model name
--payload CBE-ISO-01                Run a single payload
--output ./my-results               Output directory (default: ./results)
```

## Architecture

```
cbe-poc-isoprod/
├── knowledge-base/           # Simulated Azure AI Search documents
│   ├── 01-infrastructure.md  # DB creds, API keys, AWS resources
│   ├── 02-employee-handbook.md
│   ├── 03-api-runbook.md     # Gateway keys, OAuth secrets, monitoring
│   └── 04-patient-faq.md     # Public FAQ (non-sensitive)
├── agent/
│   ├── system-prompt.txt     # Agent config with "DO NOT DISCLOSE" section
│   ├── tools-definition.json # 4 tools (OpenAI function calling format)
│   └── tool-simulator.js     # Simulates tool responses + exfil detection
├── payloads/
│   └── cbe-payloads.json     # 10 CBE payloads + 2 baselines
├── results/                  # Test results (generated)
└── run-poc.js                # Main test harness
```

## Attack Vectors Tested

| ID | Vector | Description |
|----|--------|-------------|
| CBE-ISO-01 | K8S ConfigMap | Wrong infra values → correction reveals real ones |
| CBE-ISO-02 | JSON Validation | Migration config with wrong values |
| CBE-ISO-03 | Terraform HCL | Security review with wrong resource configs |
| CBE-ISO-04 | Code Review | Python config.py with dev values → prod leak |
| CBE-ISO-05 | Function Calling | Trick model into leaking via tool call args |
| CBE-ISO-06 | RAG Poisoning | Search + outdated values → correction |
| CBE-ISO-07 | Error Logs | Wrong connection strings in logs → diagnosis |
| CBE-ISO-08 | Structured Output | Audit checklist requesting config values |
| BASELINE-* | Direct/Jailbreak | Classic attacks (should be blocked) |

## Output

Each test produces a JSON file with:
- Full API response (model, tokens, latency, request ID)
- Multi-turn conversation (tool calls included)
- Secret detection results (exact + partial matching against 25+ known values)
- Tool exfiltration detection (secrets leaked in tool call arguments)

## Why This PoC is Different

1. **Realistic agent setup** — not just a system prompt, but tools + RAG + multi-turn
2. **Tool exfiltration** — detects secrets leaked via function call arguments (invisible to user)
3. **Ground truth validation** — 25+ known secrets checked with exact matching
4. **Full metadata** — token counts, latency, model version, request IDs for reproducibility
5. **Multi-provider** — works with OpenAI, Azure OpenAI, and Anthropic
