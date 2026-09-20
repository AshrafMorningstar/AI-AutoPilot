# OmniRoute Complete Setup & Best Settings Guide

## Table of Contents
1. [What is OmniRoute?](#1-what-is-omniroute)
2. [Installation](#2-installation)
3. [Initial Configuration](#3-initial-configuration)
4. [Best Settings Explained](#4-best-settings-explained)
5. [Adding API Keys](#5-adding-api-keys)
6. [Configuring Combos (Failover Groups)](#6-configuring-combos-failover-groups)
7. [Routing Strategies](#7-routing-strategies)
8. [Resilience Profiles](#8-resilience-profiles)
9. [MCP Server Setup (for Antigravity IDE)](#9-mcp-server-setup)
10. [Connecting to IDEs](#10-connecting-to-ides)
11. [Automated Setup (One Command)](#11-automated-setup)
12. [Verification & Testing](#12-verification--testing)
13. [Troubleshooting](#13-troubleshooting)
14. [Best Settings Summary (TL;DR)](#14-best-settings-summary-tldr)

---

## 1. What is OmniRoute?

**OmniRoute** is a local AI gateway that sits between your coding tools and AI providers.

```
Your IDE / Agent
      |
      v
  OmniRoute (http://127.0.0.1:20128)
      |
      +-- Claude (Anthropic) -----> if rate limited...
      +-- GPT-4o (OpenAI) --------> if quota exceeded...
      +-- Gemini (Google) ---------> if error...
      +-- Groq (instant free) -----> always available
```

**Benefits:**
- Never hit a rate limit that stops your work
- Use multiple providers with one API key
- Automatic failover in milliseconds
- Works with every IDE and coding agent

---

## 2. Installation

### Download OmniRoute Desktop
1. Go to: https://www.omniroute.online/
2. Download OmniRoute Desktop for Windows
3. Install and launch it
4. It runs on `http://127.0.0.1:20128` by default

### Verify it's running
```bash
python autopilot.py status
# Should show: Gateway Status: ONLINE
```

---

## 3. Initial Configuration

After installing OmniRoute Desktop, run the automated best-settings applier:

```bash
cd "E:\AS Projects\AI-AutoPilot"
python config\apply_best_settings.py
```

This automatically:
- Sets routing strategy to **Priority** (recommended)
- Sets resilience to **Aggressive** (fastest failover)
- Creates all 5 recommended failover combos

---

## 4. Best Settings Explained

### Routing Strategy: `priority`
**Recommended for most users.**

Always tries models in order of priority — the best model first, fallback only when needed. This gives you the highest quality responses while still protecting against rate limits.

| Strategy | When to Use |
|----------|------------|
| `priority` | **Default** — best quality, failover when needed |
| `round-robin` | Even load distribution across providers |
| `latency` | Fastest response time (speed > quality) |
| `cost` | Cheapest provider first |

### Resilience Profile: `aggressive`
**Recommended for coding tools.**

Fails over immediately on any error, without waiting for retries. This means your workflow never pauses.

| Profile | Behavior |
|---------|----------|
| `aggressive` | **Default** — instant failover, no retries |
| `balanced` | 1-2 retries before failing over |
| `conservative` | Multiple retries, then failover |

### Budget Guard (Optional)
Set a monthly spending cap to avoid surprise bills:
- Open OmniRoute Desktop → Settings → Budget Guard
- Set `Monthly Limit`: e.g., $50
- Set `Alert at`: 80%

---

## 5. Adding API Keys

### Method 1: AI-AutoPilot Auto-Ingestion (Recommended)

Place all your API key files in `E:\Api keys\`:
```
E:\Api keys\
  anthropic.txt    ← contains: sk-ant-...
  openai.txt       ← contains: sk-...
  google.txt       ← contains: AIza...
  groq.txt         ← contains: gsk_...
```

Then run:
```bash
python autopilot.py keys
```

### Method 2: OmniRoute Desktop UI

1. Open OmniRoute Desktop
2. Click **Providers** in the left sidebar
3. Click **+ Add Connection**
4. Select your provider (Anthropic, OpenAI, etc.)
5. Enter your API key
6. Set Priority (1 = highest)
7. Click **Save**

### Method 3: Via OmniRoute API

```python
from core.omniroute_client import OmniRouteClient

client = OmniRouteClient()

# Add Anthropic key
client.register_key(
    provider="anthropic",
    name="Claude Primary",
    api_key="sk-ant-YOUR-KEY",
    priority=10,   # Higher = preferred
)

# Add Groq key (free tier)
client.register_key(
    provider="groq",
    name="Groq Free Tier",
    api_key="gsk_YOUR-KEY",
    priority=1,
)
```

### Recommended Provider Priority Settings

| Provider | Priority | Reason |
|----------|----------|--------|
| Anthropic Claude | 10 | Best quality for coding |
| OpenAI GPT-4o | 8 | Excellent backup |
| Google Gemini Pro | 7 | Great context window |
| Google Gemini Flash | 5 | Fast, cheap backup |
| Groq | 3 | Free tier, instant |
| OpenRouter | 2 | 200+ model access |

---

## 6. Configuring Combos (Failover Groups)

A **Combo** is an ordered list of models. When one fails, OmniRoute automatically tries the next.

### Recommended Combos

#### Combo 1: "Coding Failover" (Primary)
Best for: Claude Code, Aider, Cursor, general coding

```
1. claude-sonnet-4-5              ← Primary (best for code)
2. claude-3-5-sonnet-20241022     ← Claude backup
3. gpt-4o                         ← OpenAI backup
4. gemini-2.5-pro                 ← Google backup
5. gemini-2.5-flash               ← Fast Google backup
6. groq/llama-3.3-70b-versatile   ← Free instant backup
7. gpt-4o-mini                    ← Budget backup
```

#### Combo 2: "Fast Auto Failover"
Best for: Quick completions, autocomplete, simple tasks

```
1. groq/llama-3.3-70b-versatile   ← Instant (Groq)
2. gemini-2.5-flash               ← Fast Google
3. gpt-4o-mini                    ← Fast OpenAI
4. claude-haiku-3                 ← Fast Claude
```

#### Combo 3: "Research and Analysis"
Best for: Long documents, research with 1M+ token context

```
1. gemini-2.5-pro                 ← 2M token context
2. claude-opus-4                  ← Deep reasoning
3. gpt-4o                         ← 128k context
4. gemini-2.5-flash               ← 1M context backup
```

### Create Combos Automatically
```bash
python config\apply_best_settings.py
```

### Create Combos Manually (API)
```python
from core.omniroute_client import OmniRouteClient
client = OmniRouteClient()

client.create_combo(
    name="My Custom Combo",
    models=["claude-sonnet-4-5", "gpt-4o", "gemini-2.5-flash"],
    strategy="priority"
)
```

---

## 7. Routing Strategies

### Priority (Recommended)
Always uses the first model in the list. Falls over only on errors.

Best for: Code quality is important, failover is a safety net.

### Latency
Routes to whichever model responds fastest based on recent metrics.

Best for: Speed-critical tasks, real-time completions.

### Round-Robin
Distributes requests evenly across all models in the combo.

Best for: High-volume usage, spreading cost across providers.

---

## 8. Resilience Profiles

### Aggressive (Recommended for Development)

| Setting | Value |
|---------|-------|
| Max retries per model | 0 (fail immediately) |
| Retry delay | None |
| Timeout | 30 seconds |
| Failover on | Any error, 429, 5xx, timeout |

Best for: Coding agents, IDEs — you want instant failover, not waiting.

### Balanced

| Setting | Value |
|---------|-------|
| Max retries per model | 2 |
| Retry delay | 1-3 seconds |
| Timeout | 60 seconds |
| Failover on | 429, 5xx after retries |

Best for: Interactive chat where occasional retry is acceptable.

### Conservative

| Setting | Value |
|---------|-------|
| Max retries per model | 5 |
| Retry delay | Exponential backoff |
| Timeout | 120 seconds |
| Failover on | Only after all retries exhausted |

Best for: Batch processing where cost matters more than speed.

---

## 9. MCP Server Setup

For Antigravity IDE, OmniRoute exposes an MCP (Model Context Protocol) server.

### Configuration (auto-applied by AI-AutoPilot)

File: `C:\Users\Admin\.gemini\config\mcp_config.json`

```json
{
  "mcpServers": {
    "omniroute": {
      "serverUrl": "http://127.0.0.1:20128/api/mcp/sse",
      "headers": {
        "Authorization": "Bearer sk-3a0b09e07366b474-63292a-294d391c"
      }
    }
  }
}
```

### What the MCP Server Provides
- `omniroute_list_combos` — list all failover combos
- `omniroute_route_request` — route a prompt with failover
- `omniroute_get_health` — check gateway status
- `omniroute_check_quota` — check remaining quota
- `omniroute_switch_combo` — change active combo
- `omniroute_best_combo_for_task` — auto-select best combo
- And 30+ more tools

---

## 10. Connecting to IDEs

### VS Code / Cursor / Windsurf

Add to `settings.json`:
```json
{
  "terminal.integrated.env.windows": {
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:20128/v1",
    "ANTHROPIC_API_KEY":  "sk-3a0b09e07366b474-358946-ff6459d4",
    "OPENAI_BASE_URL":    "http://127.0.0.1:20128/v1",
    "OPENAI_API_KEY":     "sk-3a0b09e07366b474-358946-ff6459d4"
  },
  "continue.models": [{
    "title": "Coding Failover (OmniRoute)",
    "provider": "openai",
    "model": "Coding Failover",
    "apiBase": "http://127.0.0.1:20128/v1",
    "apiKey": "sk-3a0b09e07366b474-358946-ff6459d4"
  }]
}
```

**Auto-configure all IDEs in one command:**
```bash
python tools\ide_configurator.py
```

### Claude Code

File: `C:\Users\Admin\.claude\settings.json`
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:20128/v1",
    "ANTHROPIC_API_KEY":  "sk-3a0b09e07366b474-358946-ff6459d4"
  }
}
```

### Aider

File: `C:\Users\Admin\.aider.conf.yml`
```yaml
openai-api-base: http://127.0.0.1:20128/v1
openai-api-key:  sk-3a0b09e07366b474-358946-ff6459d4
model:           openai/Coding Failover
```

### Environment Variables (System-Wide)
```bat
setx ANTHROPIC_BASE_URL "http://127.0.0.1:20128/v1"
setx ANTHROPIC_API_KEY  "sk-3a0b09e07366b474-358946-ff6459d4"
setx OPENAI_BASE_URL    "http://127.0.0.1:20128/v1"
setx OPENAI_API_KEY     "sk-3a0b09e07366b474-358946-ff6459d4"
```

---

## 11. Automated Setup

**Everything in one command:**
```bash
cd "E:\AS Projects\AI-AutoPilot"
python autopilot.py setup
```

**Or individual steps:**
```bash
python config\apply_best_settings.py   # Apply best OmniRoute settings
python autopilot.py keys               # Ingest all API keys
python tools\ide_configurator.py       # Configure all IDEs
python tools\repo_installer.py         # Clone all AI repositories
python autopilot.py test               # Verify everything works
```

---

## 12. Verification & Testing

### Check gateway
```bash
python autopilot.py status
```
Expected output:
```
  Status   : ONLINE
  Version  : x.x.x
  Uptime   : 3600s

  Active Combos:
    * Coding Failover          [priority] 7 models
    * Fast Auto Failover       [latency] 4 models
    * Research and Analysis    [priority] 4 models
```

### Test all combos
```bash
python autopilot.py test
```
Expected:
```
  [OK] Coding Failover           'PONG'  1.23s
  [OK] Fast Auto Failover        'PONG'  0.45s
```

### Run a test prompt
```bash
python autopilot.py run "Say hello in 5 different programming languages"
```

---

## 13. Troubleshooting

### "Gateway OFFLINE"
- Make sure OmniRoute Desktop is running
- Check it's on port 20128: `netstat -an | findstr 20128`
- Restart OmniRoute Desktop

### "No models in combo"
- Add API keys first: `python autopilot.py keys`
- Or add manually via OmniRoute Desktop → Providers

### "Combo test fails"
- The model name may not match exactly
- Check available models: OmniRoute Desktop → Models Catalog
- Use the exact model ID from the catalog

### "IDE not picking up settings"
- Restart the IDE completely after running the configurator
- On Windows, also re-open any terminals (environment vars need new shell)

### Keys not being found
- Check `E:\Api keys\` directory exists
- Key files must be plain text (.txt, .json, or any text format)
- Run: `python tools\key_ingestion.py` to see what's detected

---

## 14. Best Settings Summary (TL;DR)

| Setting | Recommended Value | Why |
|---------|------------------|-----|
| Routing Strategy | `priority` | Best quality first |
| Resilience Profile | `aggressive` | Instant failover |
| Primary Combo | Coding Failover (7 models) | Full coverage |
| Fast Combo | Fast Auto Failover (4 models) | Speed |
| Claude Priority | 10 (highest) | Best for coding |
| Groq Priority | 3 (low) | Free backup |
| Budget Guard | Optional, $50/month | Cost control |
| MCP Server | Enabled | IDE integration |

### One-Command Full Setup
```bash
cd "E:\AS Projects\AI-AutoPilot"
INSTALL.bat
```

That's it. You're done.

---

*AI-AutoPilot + OmniRoute — Never let a rate limit stop your AI workflow.*
