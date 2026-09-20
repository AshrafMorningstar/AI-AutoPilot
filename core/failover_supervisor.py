#!/usr/bin/env python3
"""
AI-AutoPilot :: Failover Supervisor
=====================================
Wraps any AI agent CLI (Claude Code, Aider, Antigravity, etc.) and:
- Monitors stdout/stderr in real time for rate-limit signals
- Automatically restarts the process on the next combo route
- Logs every failover event to progress.md
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime
from typing import List, Optional

from .omniroute_client import OMNIROUTE_URL, INFERENCE_KEY, ADMIN_KEY, FAILOVER_SIGNALS, DEFAULT_COMBOS

PROGRESS_FILE = os.environ.get("AUTOPILOT_PROGRESS", "progress.md")
MAX_RETRIES   = int(os.environ.get("AUTOPILOT_MAX_RETRIES", "5"))


def _build_env(combo_name: str) -> dict:
    """Build environment variables to inject into the child process."""
    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = f"{OMNIROUTE_URL}/v1"
    env["ANTHROPIC_API_KEY"]  = INFERENCE_KEY
    env["OPENAI_BASE_URL"]    = f"{OMNIROUTE_URL}/v1"
    env["OPENAI_API_KEY"]     = INFERENCE_KEY
    env["OMNIROUTE_URL"]      = OMNIROUTE_URL
    env["OMNIROUTE_KEY"]      = ADMIN_KEY
    env["ANTHROPIC_MODEL"]    = combo_name
    env["OPENAI_MODEL"]       = combo_name
    return env


def _log_progress(goal: str, status: str, model: str, details: str, failover: Optional[dict] = None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"# AI-AutoPilot Progress\n",
        f"**Goal**: {goal}  ",
        f"**Status**: `{status}`  ",
        f"**Active Route**: `{model}`  ",
        f"**Last Updated**: {now}\n",
    ]
    if failover:
        lines += [
            "\n### Failover Event",
            f"| Time | From | To | Reason |",
            f"| :--- | :--- | :--- | :--- |",
            f"| {now} | `{failover['from']}` | `{failover['to']}` | {failover['reason']} |\n",
        ]
    lines += [
        "\n### Details",
        details,
        "\n---",
        "*Auto-maintained by AI-AutoPilot Failover Supervisor*",
    ]
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except Exception as e:
        print(f"[Supervisor] Warning: could not write {PROGRESS_FILE}: {e}", file=sys.stderr)


def supervise(
    cmd_args: List[str],
    combos: Optional[List[str]] = None,
    goal: str = "",
) -> int:
    """
    Run cmd_args under OmniRoute supervision with automatic failover.
    Returns the final process exit code.
    """
    routes     = list(combos or DEFAULT_COMBOS)
    goal       = goal or " ".join(cmd_args)
    last_code  = -1

    for attempt, combo in enumerate(routes[:MAX_RETRIES]):
        env = _build_env(combo)
        print(f"\n[Supervisor] >> Attempt {attempt + 1}/{len(routes)} — route: '{combo}'", flush=True)
        print(f"[Supervisor] Command: {' '.join(cmd_args)}", flush=True)

        proc = subprocess.Popen(
            cmd_args,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        limit_hit = False
        output_lines: List[str] = []

        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            output_lines.append(line)
            if any(sig in line.lower() for sig in FAILOVER_SIGNALS):
                print(f"\n[Supervisor] >> Rate-limit/error detected: {line.strip()}", flush=True)
                limit_hit = True
                proc.terminate()
                break

        proc.stdout.close()
        proc.wait(timeout=10)
        last_code = proc.returncode

        if not limit_hit and last_code == 0:
            print(f"\n[Supervisor] [OK] Process completed successfully on route '{combo}'.", flush=True)
            _log_progress(goal, "COMPLETED", combo, f"Exited cleanly (code 0) on route `{combo}`.")
            return 0

        # Prepare next failover route
        next_combo = routes[(attempt + 1) % len(routes)] if attempt + 1 < len(routes) else "exhausted"
        reason     = "Rate-limit signal" if limit_hit else f"Exit code {last_code}"
        print(f"[Supervisor] [WARN] {reason}. Failing over → '{next_combo}'...", flush=True)

        _log_progress(
            goal,
            "FAILOVER",
            next_combo,
            f"{reason} on route `{combo}`. Retrying with `{next_combo}`.",
            failover={"from": combo, "to": next_combo, "reason": reason},
        )
        time.sleep(2)

    print(f"[Supervisor] [FAIL] All failover routes exhausted. Last exit code: {last_code}", flush=True)
    _log_progress(goal, "FAILED", "N/A", f"All {len(routes)} routes exhausted. Last exit: {last_code}.")
    return last_code
