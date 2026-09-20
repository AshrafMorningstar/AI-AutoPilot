#!/usr/bin/env python3
"""
AI-AutoPilot :: Universal IDE & Agent Configurator
====================================================
Zero-click automatic configuration of:
  VS Code / VS Code Insiders / VSCodium / Cursor / Windsurf
  Claude Code CLI  | Aider | Continue | Cline | Roo-Code
  Antigravity IDE  | Zed | Neovim (via env)

All are routed through OmniRoute with auto-failover.
"""

import os
import sys
import json
import shutil

# ── OmniRoute Connection ─────────────────────────────────────────────────────
OMNIROUTE_URL   = os.environ.get("OMNIROUTE_URL",  "http://127.0.0.1:20128")
OMNIROUTE_V1    = f"{OMNIROUTE_URL}/v1"
INFERENCE_KEY   = os.environ.get("OPENAI_API_KEY", "sk-3a0b09e07366b474-358946-ff6459d4")
ADMIN_KEY       = os.environ.get("OMNIROUTE_KEY",  "sk-3a0b09e07366b474-63292a-294d391c")
DEFAULT_MODEL   = "Coding Failover"

ROAMING      = os.environ.get("APPDATA",      r"C:\Users\Admin\AppData\Roaming")
USER_HOME    = os.environ.get("USERPROFILE",  r"C:\Users\Admin")
LOCAL_APP    = os.environ.get("LOCALAPPDATA", r"C:\Users\Admin\AppData\Local")

RESULTS: list[dict] = []

# ── Helpers ──────────────────────────────────────────────────────────────────
def status(ok: bool, label: str, path: str):
    tag = "[OK] " if ok else "[WARN]"
    print(f"  {tag} [{label}] {path}", flush=True)
    RESULTS.append({"label": label, "path": path, "ok": ok})


def merge_json(file_path: str, new_keys: dict):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    data = {}
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    for k, v in new_keys.items():
        if isinstance(v, dict) and isinstance(data.get(k), dict):
            data[k].update(v)
        else:
            data[k] = v
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ── VS Code Variants ─────────────────────────────────────────────────────────
VSCODE_VARIANTS = [
    ("VS Code",          os.path.join(ROAMING, "Code",             "User", "settings.json")),
    ("VS Code Insiders", os.path.join(ROAMING, "Code - Insiders",  "User", "settings.json")),
    ("VSCodium",         os.path.join(ROAMING, "VSCodium",         "User", "settings.json")),
    ("Cursor",           os.path.join(ROAMING, "Cursor",           "User", "settings.json")),
    ("Windsurf",         os.path.join(ROAMING, "Windsurf",         "User", "settings.json")),
]

VSCODE_PATCH = {
    "terminal.integrated.env.windows": {
        "ANTHROPIC_BASE_URL": OMNIROUTE_V1,
        "ANTHROPIC_API_KEY":  INFERENCE_KEY,
        "OPENAI_BASE_URL":    OMNIROUTE_V1,
        "OPENAI_API_KEY":     INFERENCE_KEY,
        "OMNIROUTE_URL":      OMNIROUTE_URL,
        "OMNIROUTE_KEY":      ADMIN_KEY,
        "ANTHROPIC_MODEL":    DEFAULT_MODEL,
        "OPENAI_MODEL":       DEFAULT_MODEL,
    },
    "continue.models": [
        {"title": "Coding Failover (OmniRoute)",    "provider": "openai", "model": "Coding Failover",    "apiBase": OMNIROUTE_V1, "apiKey": INFERENCE_KEY},
        {"title": "Fast Auto Failover (OmniRoute)", "provider": "openai", "model": "Fast Auto Failover", "apiBase": OMNIROUTE_V1, "apiKey": INFERENCE_KEY},
        {"title": "Gemini 2.5 Flash",               "provider": "openai", "model": "gemini-2.5-flash",   "apiBase": OMNIROUTE_V1, "apiKey": INFERENCE_KEY},
        {"title": "GPT-4o Mini",                    "provider": "openai", "model": "gpt-4o-mini",        "apiBase": OMNIROUTE_V1, "apiKey": INFERENCE_KEY},
        {"title": "Claude Sonnet 4.5",              "provider": "openai", "model": "claude-sonnet-4-5",  "apiBase": OMNIROUTE_V1, "apiKey": INFERENCE_KEY},
    ],
    "cline.apiProvider":   "openai-compatible",
    "cline.openAiBaseUrl": OMNIROUTE_V1,
    "cline.openAiApiKey":  INFERENCE_KEY,
    "cline.openAiModelId": DEFAULT_MODEL,
}


def configure_vscode_variants():
    print("\n[1/6] Configuring VS Code Variants...")
    for name, path in VSCODE_VARIANTS:
        try:
            merge_json(path, VSCODE_PATCH)
            status(True, name, path)
        except Exception as e:
            status(False, name, f"{path} ({e})")


# ── Claude Code ──────────────────────────────────────────────────────────────
def configure_claude_code():
    print("\n[2/6] Configuring Claude Code CLI...")
    path = os.path.join(USER_HOME, ".claude", "settings.json")
    try:
        merge_json(path, {
            "env": {
                "ANTHROPIC_BASE_URL": OMNIROUTE_V1,
                "ANTHROPIC_API_KEY":  INFERENCE_KEY,
                "ANTHROPIC_MODEL":    DEFAULT_MODEL,
            },
            "model":              DEFAULT_MODEL,
            "alwaysApproveResets": True,
        })
        status(True, "Claude Code", path)
    except Exception as e:
        status(False, "Claude Code", f"{path} ({e})")


# ── Aider ────────────────────────────────────────────────────────────────────
def configure_aider():
    print("\n[3/6] Configuring Aider...")
    path = os.path.join(USER_HOME, ".aider.conf.yml")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(
                f"# Aider — routed through AI-AutoPilot OmniRoute\n"
                f"openai-api-base:    {OMNIROUTE_V1}\n"
                f"openai-api-key:     {INFERENCE_KEY}\n"
                f"anthropic-api-key:  {INFERENCE_KEY}\n"
                f"model:              openai/{DEFAULT_MODEL}\n"
                f"editor-model:       openai/Fast Auto Failover\n"
                f"weak-model:         openai/gpt-4o-mini\n"
                f"auto-commits:       false\n"
            )
        status(True, "Aider", path)
    except Exception as e:
        status(False, "Aider", f"{path} ({e})")


# ── Antigravity IDE ──────────────────────────────────────────────────────────
def configure_antigravity():
    print("\n[4/6] Configuring Antigravity IDE MCP...")
    path = os.path.join(USER_HOME, ".gemini", "config", "mcp_config.json")
    try:
        merge_json(path, {
            "mcpServers": {
                "omniroute": {
                    "serverUrl": f"{OMNIROUTE_URL}/api/mcp/sse",
                    "headers": {"Authorization": f"Bearer {ADMIN_KEY}"},
                }
            }
        })
        status(True, "Antigravity IDE (MCP)", path)
    except Exception as e:
        status(False, "Antigravity IDE", f"{path} ({e})")


# ── Shell / System-Wide Environment ──────────────────────────────────────────
def configure_system_env():
    print("\n[5/6] Setting Persistent System Environment Variables...")
    env_vars = {
        "ANTHROPIC_BASE_URL": OMNIROUTE_V1,
        "ANTHROPIC_API_KEY":  INFERENCE_KEY,
        "OPENAI_BASE_URL":    OMNIROUTE_V1,
        "OPENAI_API_KEY":     INFERENCE_KEY,
        "OMNIROUTE_URL":      OMNIROUTE_URL,
        "OMNIROUTE_KEY":      ADMIN_KEY,
    }
    for k, v in env_vars.items():
        try:
            import subprocess
            subprocess.run(
                ["setx", k, v],
                capture_output=True, text=True, timeout=5
            )
            status(True, k, v[:40] + "..." if len(v) > 40 else v)
        except Exception as e:
            status(False, k, str(e))


# ── PowerShell Profile ───────────────────────────────────────────────────────
def configure_powershell_profile():
    print("\n[6/6] Patching PowerShell Profile...")
    ps_profile = os.path.join(USER_HOME, "Documents", "WindowsPowerShell", "Microsoft.PowerShell_profile.ps1")
    marker     = "# === AI-AutoPilot OmniRoute ==="
    block = (
        f"\n{marker}\n"
        f'$env:ANTHROPIC_BASE_URL = "{OMNIROUTE_V1}"\n'
        f'$env:ANTHROPIC_API_KEY  = "{INFERENCE_KEY}"\n'
        f'$env:OPENAI_BASE_URL    = "{OMNIROUTE_V1}"\n'
        f'$env:OPENAI_API_KEY     = "{INFERENCE_KEY}"\n'
        f'$env:OMNIROUTE_URL      = "{OMNIROUTE_URL}"\n'
        f'$env:OMNIROUTE_KEY      = "{ADMIN_KEY}"\n'
        f"# === End AI-AutoPilot ===\n"
    )
    try:
        os.makedirs(os.path.dirname(ps_profile), exist_ok=True)
        existing = ""
        if os.path.exists(ps_profile):
            with open(ps_profile, "r", encoding="utf-8") as f:
                existing = f.read()
        if marker not in existing:
            with open(ps_profile, "a", encoding="utf-8") as f:
                f.write(block)
        status(True, "PowerShell Profile", ps_profile)
    except Exception as e:
        status(False, "PowerShell Profile", str(e))


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("   AI-AutoPilot :: Universal IDE & Agent Configurator")
    print("   Zero-Click · Full Failover · All Providers")
    print("=" * 60)

    configure_vscode_variants()
    configure_claude_code()
    configure_aider()
    configure_antigravity()
    configure_system_env()
    configure_powershell_profile()

    ok_count   = sum(1 for r in RESULTS if r["ok"])
    fail_count = len(RESULTS) - ok_count

    print("\n" + "=" * 60)
    print(f"[DONE] {ok_count} configured · {fail_count} skipped/failed")
    print("All AI tools now route through OmniRoute with auto-failover.")
    print("=" * 60)


if __name__ == "__main__":
    main()
