# 🤖 AI-AutoPilot — Zero-Click AI Agent Failover & Automation

> **Never hit an AI rate limit again.** AI-AutoPilot automatically switches between Claude, GPT-4, Gemini, Groq, and 15+ AI providers the moment you hit a quota or error — with **zero clicks**.

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)](https://python.org)
[![OmniRoute Powered](https://img.shields.io/badge/powered%20by-OmniRoute-purple.svg)](https://omniroute.online)
[![Windows](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#)
[![VS Code](https://img.shields.io/badge/IDE-VS%20Code%20%7C%20Cursor%20%7C%20Claude%20Code-blue.svg)](#supported-ides)

---

## 🚀 What is AI-AutoPilot?

**AI-AutoPilot** is a fully automated AI agent orchestrator powered by [OmniRoute](https://omniroute.online). It:

- 🔄 **Auto-switches AI models** when you hit rate limits, quotas, or errors
- ⚡ **Zero-click setup** — one command configures everything
- 🛠️ **Configures every IDE automatically** — VS Code, Cursor, Claude Code, Aider, and more
- 🔑 **Ingests all your API keys** from a single folder, auto-detecting the provider
- 📦 **Installs 20+ AI tool repositories** automatically
- 📊 **Real-time progress tracking** with automatic failover logging

### Supported AI Providers
| Provider | Models |
|----------|--------|
| Anthropic | Claude 3.5 Sonnet, Claude 4, Claude Opus |
| OpenAI | GPT-4o, GPT-4o-mini, GPT-4 Turbo |
| Google | Gemini 2.5 Pro, Gemini 2.5 Flash, Gemini Ultra |
| Groq | Llama 3, Mixtral, Gemma (blazing fast) |
| NVIDIA NIM | Llama 3, Nemotron |
| xAI | Grok-2, Grok-3 |
| OpenRouter | 200+ models |
| + More | Auto-detected from your API keys |

---

## ⚡ Quick Start (One Command)

### Windows
```bat
git clone https://github.com/AshrafMorningstar/AI-AutoPilot.git
cd AI-AutoPilot
INSTALL.bat
```

### macOS / Linux / WSL
```bash
git clone https://github.com/AshrafMorningstar/AI-AutoPilot.git
cd AI-AutoPilot
chmod +x install.sh && ./install.sh
```

**That's it.** AI-AutoPilot will:
1. Scan your API key folder and register all keys in OmniRoute
2. Configure every installed IDE and coding agent automatically
3. Clone all 20+ AI repositories to `~/ai_repositories`
4. Run a health test to verify everything works

---

## 🛠️ Supported IDEs & Coding Agents

| Tool | Auto-Configured? |
|------|-----------------|
| VS Code | ✅ Yes |
| VS Code Insiders | ✅ Yes |
| VSCodium | ✅ Yes |
| Cursor | ✅ Yes |
| Windsurf | ✅ Yes |
| Claude Code CLI | ✅ Yes |
| Aider | ✅ Yes |
| Continue Extension | ✅ Yes |
| Cline / Roo-Code | ✅ Yes |
| Antigravity IDE | ✅ Yes |
| PowerShell Profile | ✅ Yes |

---

## 💻 CLI Commands

```bash
# Full zero-click setup
python autopilot.py setup

# Check gateway health + active combos
python autopilot.py status

# Run a prompt with auto-failover across all providers
python autopilot.py run "Write a Python HTTP server"

# Supervise any agent CLI — auto-failover on rate limits
python autopilot.py wrap claude --print "fix this bug"
python autopilot.py wrap aider --model openai/gpt-4o

# Ingest all API keys from E:\Api keys
python autopilot.py keys

# Clone / update all AI repositories
python autopilot.py repos

# View current execution progress
python autopilot.py progress

# Test all failover combos
python autopilot.py test
```

---

## 📁 Project Structure

```
AI-AutoPilot/
├── autopilot.py              ← Master CLI entry point
├── INSTALL.bat               ← Windows one-click installer
├── install.sh                ← Unix one-click installer
├── core/
│   ├── omniroute_client.py   ← OmniRoute API client with failover
│   └── failover_supervisor.py ← Real-time agent process supervisor
├── tools/
│   ├── ide_configurator.py  ← Universal IDE & agent configurator
│   ├── repo_installer.py    ← AI repository ecosystem installer
│   └── key_ingestion.py     ← API key scanner & OmniRoute registration
├── docs/
│   └── TUTORIAL.md          ← Full setup & usage guide
└── .github/
    └── workflows/ci.yml     ← GitHub Actions CI
```

---

## 🔑 API Key Setup

Place your API key files in `E:\Api keys` (Windows) or `~/api_keys` (Unix).  
AI-AutoPilot auto-detects the provider from the key format:

| Key Prefix | Provider |
|------------|----------|
| `sk-ant-*` | Anthropic |
| `sk-*` | OpenAI |
| `AIza*` | Google Gemini |
| `gsk_*` | Groq |
| `nvapi-*` | NVIDIA NIM |
| `xai-*` | xAI / Grok |
| `or-*` | OpenRouter |

---

## 🔄 How Auto-Failover Works

```
Your Agent → OmniRoute → Combo "Coding Failover"
                              ├─ Claude Sonnet 4.5  ← try first
                              ├─ GPT-4o             ← rate limited? switch
                              ├─ Gemini 2.5 Flash   ← still failing? switch
                              └─ Groq Llama 3       ← instant fallback
```

When AI-AutoPilot detects a **rate limit, quota error, or connection failure**, it:
1. Instantly switches to the next model in your combo
2. Restarts your agent command with the new model
3. Logs the failover event to `progress.md`
4. Never stops your workflow

---

## 📖 Full Tutorial

See [docs/TUTORIAL.md](docs/TUTORIAL.md) for:
- Step-by-step setup guide
- How to add your API keys
- How to customize failover combos
- How to use with Claude Code, Aider, and Cursor
- Troubleshooting common issues

---

## 🌟 Why AI-AutoPilot?

| Problem | AI-AutoPilot Solution |
|---------|----------------------|
| Hit Claude rate limit mid-task | Auto-switches to GPT-4o instantly |
| OpenAI quota exceeded | Falls back to Gemini 2.5 Flash |
| Groq overloaded | Retries with NVIDIA NIM |
| Model unavailable | Cycles through 15+ providers |
| Manual IDE config | Zero-click auto-configuration |
| Managing 50+ API keys | One folder, auto-detected |

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](.github/CONTRIBUTING.md).

1. Fork the repo
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m "Add my feature"`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🔗 Related Projects

- [OmniRoute](https://github.com/diegosouzapw/OmniRoute) — The multi-provider AI gateway
- [Claude Code](https://claude.ai/code) — Anthropic's coding agent
- [Continue](https://continue.dev) — VS Code AI extension
- [Aider](https://aider.chat) — AI pair programming in the terminal

---

<div align="center">

**⭐ Star this repo if AI-AutoPilot saved your workflow! ⭐**

[![GitHub stars](https://img.shields.io/github/stars/AshrafMorningstar/AI-AutoPilot?style=social)](https://github.com/AshrafMorningstar/AI-AutoPilot)

</div>

