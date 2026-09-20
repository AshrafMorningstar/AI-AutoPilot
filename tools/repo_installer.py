#!/usr/bin/env python3
"""
AI-AutoPilot :: Repository Ecosystem Installer
================================================
Clones and maintains all AI tool repositories automatically.
Supports shallow clone, auto-update on re-run, and manifest generation.
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from typing import List, Dict, Tuple

TARGET_DIR = os.environ.get("AUTOPILOT_REPOS", r"C:\Users\Admin\ai_repositories")

# ── Git binary detection ──────────────────────────────────────────────────────
def _find_git() -> str:
    candidates = [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files (x86)\Git\cmd\git.exe",
        r"C:\Users\Admin\AppData\Local\GitHubDesktop\app-3.6.6\resources\app\git\cmd\git.exe",
        "git",
    ]
    for c in candidates:
        if c == "git" or os.path.isfile(c):
            return c
    return "git"

GIT = _find_git()

# ── Repository catalogue ──────────────────────────────────────────────────────
REPOSITORIES: List[Dict] = [
    # OmniRoute & routing
    {"name": "OmniRoute",              "url": "https://github.com/diegosouzapw/OmniRoute.git",               "desc": "Multi-provider AI gateway"},
    # Claude ecosystem
    {"name": "ECC",                    "url": "https://github.com/affaan-m/ECC.git",                         "desc": "Everything Claude Code configurations"},
    {"name": "claude-mem",             "url": "https://github.com/thedotmack/claude-mem.git",                "desc": "Persistent memory compiler for Claude"},
    # Spec & planning
    {"name": "spec-kit",               "url": "https://github.com/github/spec-kit.git",                      "desc": "GitHub Spec-Driven Development toolkit"},
    # Context & memory
    {"name": "headroom",               "url": "https://github.com/headroomlabs-ai/headroom.git",             "desc": "Token & context window headroom manager"},
    {"name": "codebase-memory-mcp",    "url": "https://github.com/DeusData/codebase-memory-mcp.git",         "desc": "Codebase semantic memory MCP server"},
    {"name": "graphify",               "url": "https://github.com/Graphify-Labs/graphify.git",               "desc": "Codebase knowledge graph extractor"},
    {"name": "archify",                "url": "https://github.com/tt-a1i/archify.git",                       "desc": "Architecture decision record generator"},
    # Agent frameworks
    {"name": "Graft",                  "url": "https://github.com/trailhq/Graft.git",                        "desc": "Fast multi-agent scaffolding engine"},
    {"name": "agency-agents",          "url": "https://github.com/msitarzewski/agency-agents.git",           "desc": "Specialized multi-agent personas"},
    {"name": "agentation",             "url": "https://github.com/benjitaylor/agentation.git",               "desc": "Visual annotation bridge for agents"},
    {"name": "ponytail",               "url": "https://github.com/DietrichGebert/ponytail.git",              "desc": "Task queue & session manager"},
    {"name": "agent-skills",           "url": "https://github.com/addyosmani/agent-skills.git",             "desc": "Production agent skills collection"},
    # Free LLM APIs
    {"name": "awesome-freellm-apis",   "url": "https://github.com/open-free-llm-api/awesome-freellm-apis.git", "desc": "Curated free LLM API catalog"},
    {"name": "freellmapi",             "url": "https://github.com/tashfeenahmed/freellmapi.git",             "desc": "Free LLM API proxy"},
    # Security & sandbox
    {"name": "strix",                  "url": "https://github.com/usestrix/strix.git",                       "desc": "Agent security & sandbox runtime"},
    # Web scraping
    {"name": "Scrapling",              "url": "https://github.com/D4Vinci/Scrapling.git",                    "desc": "Undetected anti-bot web scraper"},
    {"name": "agent-reach",            "url": "https://github.com/Panniantong/agent-reach.git",             "desc": "Web search & deep fetch engine"},
    # Multimodal
    {"name": "OpenMontage",            "url": "https://github.com/calesthio/OpenMontage.git",               "desc": "Multi-modal composition toolkit"},
    # Misc skills
    {"name": "one-skill-to-rule-them-all", "url": "https://github.com/rebelytics/one-skill-to-rule-them-all.git", "desc": "Universal meta-skill orchestrator"},
    {"name": "claude-code-setup",      "url": "https://github.com/rse/claude-code-setup.git",               "desc": "Claude Code environment setups"},
]


def _run_git(args: List[str], cwd: str = None, timeout: int = 60) -> Tuple[int, str, str]:
    try:
        r = subprocess.run(
            [GIT] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Timed out"
    except Exception as e:
        return -2, "", str(e)


def clone_or_update(repo: Dict) -> Tuple[bool, str]:
    name = repo["name"]
    url  = repo["url"]
    dest = os.path.join(TARGET_DIR, name)

    if os.path.isdir(os.path.join(dest, ".git")):
        code, out, err = _run_git(["pull", "--ff-only"], cwd=dest)
        if code == 0:
            return True, f"Updated  → {out or 'already up to date'}"
        return True, f"Pull warn (kept): {err[:80]}"
    else:
        code, out, err = _run_git(["clone", "--depth", "1", url, dest])
        if code == 0:
            return True, "Cloned ✓"
        return False, f"Clone failed: {err[:120]}"


def main():
    os.makedirs(TARGET_DIR, exist_ok=True)
    print("=" * 62)
    print("   AI-AutoPilot :: Repository Ecosystem Installer")
    print(f"   Target : {TARGET_DIR}")
    print(f"   Repos  : {len(REPOSITORIES)}")
    print("=" * 62)

    manifest = {}
    ok = fail = 0

    for idx, repo in enumerate(REPOSITORIES, 1):
        name = repo["name"]
        desc = repo["desc"]
        print(f"\n  ({idx:02d}/{len(REPOSITORIES)}) {name:<35} {desc}")
        success, msg = clone_or_update(repo)
        status = "OK" if success else "FAILED"
        icon   = "[OK]" if success else "[FAIL]"
        print(f"             {icon} {msg}")
        manifest[name] = {
            "status":  status,
            "message": msg,
            "path":    os.path.join(TARGET_DIR, name),
            "url":     repo["url"],
            "desc":    desc,
        }
        (ok if success else fail)
        if success:
            ok += 1
        else:
            fail += 1
        time.sleep(0.3)

    # Write manifest
    manifest_path = os.path.join(TARGET_DIR, "ecosystem_manifest.json")
    manifest["_meta"] = {
        "generated_at": datetime.now().isoformat(),
        "total": len(REPOSITORIES),
        "ok": ok,
        "failed": fail,
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("\n" + "=" * 62)
    print(f"  [OK] {ok} cloned/updated  |  [FAIL] {fail} failed")
    print(f"  Manifest: {manifest_path}")
    print("=" * 62)


if __name__ == "__main__":
    main()
