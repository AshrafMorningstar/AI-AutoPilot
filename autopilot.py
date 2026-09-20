#!/usr/bin/env python3
"""
AI-AutoPilot :: Master CLI  (autopilot)
=========================================
The single entry point for everything:

  autopilot setup          Zero-click full setup of all IDEs, keys, repos
  autopilot status         Gateway health + active combos
  autopilot run <prompt>   Run AI prompt with auto-failover
  autopilot wrap <cmd>     Supervise any AI agent CLI with failover
  autopilot keys           Ingest all API keys from E:\\Api keys
  autopilot repos          Clone / update all AI repositories
  autopilot progress       Show current progress.md
  autopilot test           Run self-test (ping all combos)

Zero dependencies beyond Python 3.8+.
"""

import sys
import os
import json
import time
import subprocess
from pathlib import Path

# ── Resolve project root ──────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from core.omniroute_client import OmniRouteClient, DEFAULT_COMBOS, OMNIROUTE_URL, INFERENCE_KEY, ADMIN_KEY
from core.failover_supervisor import supervise

PROGRESS_FILE = "progress.md"


# ── Sub-command helpers ──────────────────────────────────────────────────────
def _run_tool(module_path: str, *args):
    """Run a tool script in a subprocess, forwarding output."""
    cmd = [sys.executable, str(ROOT / module_path)] + list(args)
    result = subprocess.run(cmd)
    return result.returncode


def cmd_setup(_args):
    """Run full zero-click setup: keys → IDEs → repos → health test."""
    print("\n" + "=" * 64)
    print("  AI-AutoPilot :: Full Zero-Click Setup")
    print("=" * 64)

    steps = [
        ("Ingesting API Keys",         "tools/key_ingestion.py"),
        ("Configuring IDEs & Agents",  "tools/ide_configurator.py"),
        ("Cloning AI Repositories",    "tools/repo_installer.py"),
    ]

    all_ok = True
    for title, path in steps:
        print(f"\n>>>  {title}...")
        code = _run_tool(path)
        if code != 0:
            print(f"   [WARN]  {title} finished with warnings (exit {code})")
            all_ok = False

    # Health test
    print("\n>>>  Running Gateway Health Test...")
    cmd_test([])

    print("\n" + "=" * 64)
    print("  [OK] AI-AutoPilot setup complete!")
    print(f"  Gateway : {OMNIROUTE_URL}")
    print(f"  CLI     : python autopilot.py <command>")
    print("=" * 64)


def cmd_status(_args):
    client = OmniRouteClient()
    print("\n" + "=" * 56)
    print("  AI-AutoPilot :: Gateway Status")
    print("=" * 56)

    code, data = client.get_health()
    if code == 200:
        print(f"  Status   : ONLINE [OK]")
        if isinstance(data, dict):
            print(f"  Version  : {data.get('version', 'unknown')}")
            print(f"  Uptime   : {float(data.get('uptime', 0)):.0f}s")
    else:
        print(f"  Status   : OFFLINE [FAIL] ({data})")
        return

    print("\n  Active Combos:")
    _, combos_data = client.list_combos()
    if isinstance(combos_data, list):
        for c in combos_data:
            name  = c.get("name", "?")
            strat = c.get("strategy", "?")
            mods  = len(c.get("models", []))
            print(f"    • {name:<30} [{strat}] {mods} models")
    else:
        print(f"  (Could not list combos: {combos_data})")

    print("\n  Environment:")
    print(f"    OMNIROUTE_URL   : {OMNIROUTE_URL}")
    print(f"    INFERENCE_KEY   : {INFERENCE_KEY[:14]}...")
    print(f"    ADMIN_KEY       : {ADMIN_KEY[:14]}...")
    print("=" * 56)


def cmd_test(_args):
    client = OmniRouteClient()
    print("\n  Testing failover combos...")
    for combo in DEFAULT_COMBOS:
        t0 = time.time()
        try:
            result = client.chat_with_failover("Respond with exactly: PONG", combos=[combo], max_tokens=10)
            elapsed = time.time() - t0
            icon    = "[OK]" if result and "PONG" in result.upper() else "[WARN] "
            print(f"  {icon} {combo:<30} {result!r:<12} {elapsed:.2f}s")
        except Exception as e:
            print(f"  [FAIL] {combo:<30} error: {e}")


def cmd_run(args):
    if not args:
        print("[autopilot] Usage: autopilot run <your prompt here>")
        sys.exit(1)
    prompt = " ".join(args)
    client = OmniRouteClient()
    print(f"\n[autopilot] Running: {prompt[:80]}...\n")
    result = client.chat_with_failover(prompt)
    if result:
        print(result)
    else:
        print("[autopilot] All routes failed. Check 'autopilot status'.")
        sys.exit(1)


def cmd_wrap(args):
    if not args:
        print("[autopilot] Usage: autopilot wrap <cli-command> [args...]")
        sys.exit(1)
    sys.exit(supervise(args, goal=f"wrap: {' '.join(args)}"))


def cmd_keys(_args):
    _run_tool("tools/key_ingestion.py")


def cmd_repos(_args):
    _run_tool("tools/repo_installer.py")


def cmd_progress(_args):
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print(f"[autopilot] No {PROGRESS_FILE} found in: {os.getcwd()}")


def cmd_help(_args):
    print(__doc__)


# ── Dispatch table ────────────────────────────────────────────────────────────
COMMANDS = {
    "setup":    cmd_setup,
    "status":   cmd_status,
    "test":     cmd_test,
    "run":      cmd_run,
    "wrap":     cmd_wrap,
    "keys":     cmd_keys,
    "repos":    cmd_repos,
    "progress": cmd_progress,
    "help":     cmd_help,
    "--help":   cmd_help,
    "-h":       cmd_help,
}


def main():
    if len(sys.argv) < 2:
        cmd_help([])
        sys.exit(0)

    command = sys.argv[1].lower()
    rest    = sys.argv[2:]

    handler = COMMANDS.get(command)
    if handler:
        handler(rest)
    else:
        # Treat unknown command as a prompt shorthand
        cmd_run(sys.argv[1:])


if __name__ == "__main__":
    main()
