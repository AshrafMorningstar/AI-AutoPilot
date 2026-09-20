#!/usr/bin/env python3
"""
AI-AutoPilot :: OmniRoute Best Settings Applier
=================================================
Applies the recommended OmniRoute configuration automatically:
  - Sets routing strategy to 'priority'
  - Sets resilience profile to 'aggressive'
  - Creates all recommended failover combos
  - Validates gateway connectivity

Run: python config/apply_best_settings.py
"""

import sys
import os
import json
import time
import urllib.request
import urllib.error

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.omniroute_client import OmniRouteClient

# ── Best Combos Definition ────────────────────────────────────────────────────
BEST_COMBOS = [
    {
        "name": "Coding Failover",
        "strategy": "priority",
        "models": [
            "claude-sonnet-4-5",
            "claude-3-5-sonnet-20241022",
            "gpt-4o",
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "groq/llama-3.3-70b-versatile",
            "gpt-4o-mini",
        ],
        "desc": "Primary coding combo — best quality with full failover chain",
    },
    {
        "name": "Fast Auto Failover",
        "strategy": "latency",
        "models": [
            "groq/llama-3.3-70b-versatile",
            "gemini-2.5-flash",
            "gpt-4o-mini",
            "claude-haiku-3",
        ],
        "desc": "Fastest responses — latency-optimized, great for autocomplete",
    },
    {
        "name": "Research and Analysis",
        "strategy": "priority",
        "models": [
            "gemini-2.5-pro",
            "claude-opus-4",
            "gpt-4o",
            "gemini-2.5-flash",
        ],
        "desc": "Long documents, research, analysis — maximum context window",
    },
    {
        "name": "Vision Tasks",
        "strategy": "priority",
        "models": [
            "gpt-4o",
            "claude-sonnet-4-5",
            "gemini-2.5-pro",
        ],
        "desc": "Image understanding, screenshots, diagrams",
    },
    {
        "name": "Free Tier Only",
        "strategy": "round-robin",
        "models": [
            "groq/llama-3.3-70b-versatile",
            "groq/mixtral-8x7b",
            "gemini-2.5-flash",
        ],
        "desc": "Zero-cost usage — free-tier models only",
    },
]


def _print(msg: str, level: str = "INFO"):
    icons = {"INFO": "  [*]", "OK": "  [OK]", "WARN": "  [!!]", "FAIL": "  [XX]", "HEAD": ""}
    print(f"{icons.get(level, '  ')} {msg}", flush=True)


def apply_settings(client: OmniRouteClient):
    print("=" * 62)
    print("  AI-AutoPilot :: OmniRoute Best Settings Applier")
    print("=" * 62)

    # ── 1. Health check ───────────────────────────────────────────────────────
    _print("Checking gateway connectivity...", "INFO")
    code, data = client.get_health()
    if code != 200:
        _print(f"Gateway OFFLINE (HTTP {code}). Is OmniRoute Desktop running?", "FAIL")
        _print("Start OmniRoute Desktop, then re-run this script.", "WARN")
        return False
    _print(f"Gateway ONLINE — {data.get('version', 'v?')}", "OK")

    # ── 2. Routing strategy ───────────────────────────────────────────────────
    _print("Setting routing strategy -> 'priority'...", "INFO")
    code, resp = client.set_strategy("priority")
    if code in (200, 201, 204):
        _print("Routing strategy set to 'priority'", "OK")
    else:
        _print(f"Strategy set returned HTTP {code}: {str(resp)[:80]}", "WARN")

    # ── 3. Resilience profile ─────────────────────────────────────────────────
    _print("Setting resilience profile -> 'aggressive'...", "INFO")
    code, resp = client.set_resilience("aggressive")
    if code in (200, 201, 204):
        _print("Resilience profile set to 'aggressive'", "OK")
    else:
        _print(f"Resilience set returned HTTP {code}: {str(resp)[:80]}", "WARN")

    # ── 4. Get existing combos (build name->id map) ───────────────────────────
    _print("Loading existing combos...", "INFO")
    code, existing = client.list_combos()
    existing_names = {}
    if code == 200 and isinstance(existing, list):
        for c in existing:
            name = c.get("name", "")
            cid  = c.get("id", "") or c.get("_id", "")
            if name:
                existing_names[name] = cid
        _print(f"Found {len(existing_names)} existing combo(s): {list(existing_names.keys())}", "INFO")

    # ── 5. Create / update all combos ────────────────────────────────────────
    # OmniRoute only accepts "priority" or "round-robin" strategies
    VALID_STRATEGIES = {"priority", "round-robin"}

    print()
    _print("Creating / updating best-practice combos...", "INFO")
    created = updated = failed = 0

    for combo in BEST_COMBOS:
        name     = combo["name"]
        models   = combo["models"]
        strategy = combo["strategy"] if combo["strategy"] in VALID_STRATEGIES else "priority"
        desc     = combo["desc"]

        if name in existing_names:
            cid  = existing_names[name]
            if cid:
                code, resp = client.update_combo(cid, name, models, strategy)
                action = "Updated"
            else:
                # ID unknown — try delete+create pattern by attempting create
                code, resp = client.create_combo(name, models, strategy)
                action = "Created(re)"
        else:
            code, resp = client.create_combo(name, models, strategy)
            action = "Created"

        if code in (200, 201):
            _print(f"{action}: '{name}' ({len(models)} models, {strategy})", "OK")
            _print(f"       {desc}", "INFO")
            if "Created" in action:
                created += 1
            else:
                updated += 1
        elif code == 400 and isinstance(resp, dict) and "already exists" in str(resp).lower():
            # Already exists and we couldn't update — that's OK, it's there
            _print(f"Already exists (OK): '{name}'", "OK")
            updated += 1
        else:
            _print(f"FAILED '{name}': HTTP {code} — {str(resp)[:80]}", "WARN")
            failed += 1

        time.sleep(0.3)

    # ── 6. Final verification ─────────────────────────────────────────────────
    print()
    _print("Verifying final combo list...", "INFO")
    code, final = client.list_combos()
    if code == 200 and isinstance(final, list):
        for c in final:
            name    = c.get("name", "?")
            strat   = c.get("strategy", "?")
            n_models = len(c.get("models", []))
            _print(f"  Combo: '{name}' [{strat}] {n_models} models", "OK")

    print()
    print("=" * 62)
    print(f"  Settings Applied: {created} created | {updated} updated | {failed} failed")
    print()
    print("  Recommended next steps:")
    print("  1. Add your provider API keys:  python autopilot.py keys")
    print("  2. Test all combos:             python autopilot.py test")
    print("  3. Configure your IDEs:         python autopilot.py setup")
    print("=" * 62)
    return True


def main():
    client = OmniRouteClient()
    success = apply_settings(client)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
