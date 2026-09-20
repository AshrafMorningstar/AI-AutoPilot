# AI-AutoPilot Tutorial & Setup Guide

## Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [One-Click Installation](#2-one-click-installation)
3. [Manual Installation](#3-manual-installation)
4. [Adding API Keys](#4-adding-api-keys)
5. [Using the CLI](#5-using-the-cli)
6. [IDE Configuration](#6-ide-configuration)
7. [Auto-Failover Explained](#7-auto-failover-explained)
8. [Customizing Failover Combos](#8-customizing-failover-combos)
9. [Using with Claude Code](#9-using-with-claude-code)
10. [Using with Aider](#10-using-with-aider)
11. [Using with Cursor / VS Code](#11-using-with-cursor--vs-code)
12. [Troubleshooting](#12-troubleshooting)
13. [Progress File](#13-progress-file)

---

## 1. Prerequisites

- **Python 3.8+** — [Download](https://www.python.org/downloads/)
- **OmniRoute Desktop** running on `http://127.0.0.1:20128`
- **Git** (optional, for cloning repositories)
- API keys for at least one AI provider

---

## 2. One-Click Installation

### Windows
```bat
INSTALL.bat
```
Double-click `INSTALL.bat` or run it from Command Prompt. It will:
- Configure all your IDEs
- Ingest all API keys from `E:\Api keys`
- Clone all AI tool repositories
- Run a health check

### macOS / Linux / WSL
```bash
./install.sh
```

---

## 3. Manual Installation

If you prefer to run each step manually:

```bash
# Step 1: Ingest API keys
python autopilot.py keys

# Step 2: Configure all IDEs
python autopilot.py repos
# Actually configure IDEs:
python tools/ide_configurator.py

# Step 3: Clone repositories
python tools/repo_installer.py

# Step 4: Health check
python autopilot.py status
```

---

## 4. Adding API Keys

### Option A: Key Folder (Recommended)
Place your API key files in `E:\Api keys` (Windows) or `~/api_keys` (Unix).

**Supported file formats:**
- Plain text files with one key per line
- JSON files with keys as values
- Any text file — AI-AutoPilot auto-extracts keys by pattern

**Example `E:\Api keys\anthropic.txt`:**
```
sk-ant-api03-YOUR-KEY-HERE
```

**Example `E:\Api keys\openai.txt`:**
```
sk-YOUR-OPENAI-KEY-HERE
```

Then run:
```bash
python autopilot.py keys
```

### Option B: Environment Variables
```bash
set ANTHROPIC_API_KEY=sk-ant-YOUR-KEY
set OPENAI_API_KEY=sk-YOUR-KEY
```

### Option C: OmniRoute Desktop
Open OmniRoute Desktop → Providers → Add Connection manually.

---

## 5. Using the CLI

### Run a prompt with auto-failover
```bash
python autopilot.py run "Write a REST API in Python with FastAPI"
```

### Supervise any AI agent
```bash
# Wrap Claude Code
python autopilot.py wrap claude --print "Refactor this codebase"

# Wrap Aider
python autopilot.py wrap aider --model openai/gpt-4o my_file.py

# Wrap any custom command
python autopilot.py wrap my_ai_script.py
```

When wrapped, AI-AutoPilot monitors the process output. If it detects:
- `429 Too Many Requests`
- `rate limit exceeded`
- `quota exceeded`
- `connection reset`
- ...or any similar error

It **automatically restarts** the command with the next AI model in your failover combo.

### Check gateway status
```bash
python autopilot.py status
```

### View progress log
```bash
python autopilot.py progress
```

---

## 6. IDE Configuration

AI-AutoPilot automatically configures these files:

| IDE | Config File Modified |
|-----|---------------------|
| VS Code | `%APPDATA%\Code\User\settings.json` |
| Cursor | `%APPDATA%\Cursor\User\settings.json` |
| Claude Code | `~\.claude\settings.json` |
| Aider | `~\.aider.conf.yml` |
| Antigravity | `~\.gemini\config\mcp_config.json` |
| PowerShell | `Documents\WindowsPowerShell\profile.ps1` |

After running `python autopilot.py setup`, **restart your IDE** for changes to take effect.

---

## 7. Auto-Failover Explained

AI-AutoPilot uses **OmniRoute Combos** — ordered lists of AI models.

**Default "Coding Failover" combo:**
```
1. Claude Sonnet 4.5  (primary)
2. GPT-4o             (first backup)
3. Gemini 2.5 Flash   (second backup)
4. Groq Llama 3       (fast backup)
5. gpt-4o-mini        (budget backup)
```

When a model fails, OmniRoute instantly routes to the next one. Your code and workflow **never stop**.

---

## 8. Customizing Failover Combos

Edit combos via the OmniRoute Desktop UI, or use the API:

```python
from core.omniroute_client import OmniRouteClient

client = OmniRouteClient()

# Create a custom combo
client.create_combo(
    name="My Custom Failover",
    models=["claude-sonnet-4-5", "gpt-4o", "gemini-2.5-pro"],
    strategy="priority"
)
```

Then use your custom combo:
```bash
python autopilot.py run "Your prompt" --combo "My Custom Failover"
```

---

## 9. Using with Claude Code

After running `python autopilot.py setup`, Claude Code is automatically configured.

```bash
# Use Claude Code normally — failover is automatic
claude --print "Help me debug this"

# Or use the supervisor for explicit failover tracking
python autopilot.py wrap claude --print "Help me debug this"
```

Claude Code will use OmniRoute at `http://127.0.0.1:20128/v1` as its backend.

---

## 10. Using with Aider

```bash
# Aider is auto-configured to use OmniRoute
aider my_file.py

# Or explicitly:
aider --openai-api-base http://127.0.0.1:20128/v1 \
      --openai-api-key sk-your-key \
      --model openai/Coding\ Failover \
      my_file.py
```

---

## 11. Using with Cursor / VS Code

After running setup:
1. **Restart Cursor / VS Code**
2. Open any AI extension (Continue, Cline, etc.)
3. The model dropdown will show: **Coding Failover (OmniRoute)**
4. Select it — all requests now route through OmniRoute with auto-failover

The terminal in VS Code/Cursor also has the environment variables pre-configured.

---

## 12. Troubleshooting

### OmniRoute is offline
```bash
python autopilot.py status
# Should show "ONLINE" — if OFFLINE, start OmniRoute Desktop first
```

### "No module named 'core'"
Run autopilot.py from the project root:
```bash
cd E:\AS Projects\AI-AutoPilot
python autopilot.py status
```

### Keys not being detected
Check your `E:\Api keys` directory exists and contains text files with API keys.
Run `python autopilot.py keys` to see what was found.

### Rate limits still occurring
Make sure your OmniRoute combo has multiple working models:
```bash
python autopilot.py test
```
Any combo that returns "PONG" is working.

---

## 13. Progress File

AI-AutoPilot writes a `progress.md` file tracking:
- Current task goal
- Active model/route
- All failover events with timestamps
- Final completion status

```bash
python autopilot.py progress
```

Example output:
```markdown
# AI-AutoPilot Progress

**Goal**: Write a REST API in Python...
**Status**: `COMPLETED`
**Active Route**: `gemini-2.5-flash`
**Last Updated**: 2026-09-20 14:30:00

### Failover Event
| Time | From | To | Reason |
| 14:29:55 | `claude-sonnet-4-5` | `gpt-4o` | Rate-limit signal |
| 14:30:01 | `gpt-4o` | `gemini-2.5-flash` | Rate-limit signal |
```

---

*AI-AutoPilot — Never let a rate limit stop your AI workflow.*
