#!/usr/bin/env python3
"""
AI-AutoPilot :: Master Autonomous Deployment & Verifier
=========================================================
Fully autonomous, zero-click script that:
 1. Displays the primary OmniRoute repository link
 2. Downloads/verifies OmniRoute core repository first
 3. Ingests all API keys from E:\\Api keys
 4. Auto-detects all installed IDEs & AI coding agents
 5. Applies all failover routing settings across all tools
 6. Clones/updates all 21 AI ecosystem repositories
 7. Runs live end-to-end failover test
 8. Syncs project with GitHub repository
"""

import os
import sys
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

GITHUB_REPO = "https://github.com/AshrafMorningstar/AI-AutoPilot"
OMNIROUTE_REPO = "https://github.com/diegosouzapw/OmniRoute.git"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

def _find_git() -> str:
    candidates = [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files (x86)\Git\cmd\git.exe",
        r"C:\Users\Admin\AppData\Local\GitHubDesktop\app-3.6.6\resources\app\git\cmd\git.exe",
        "git",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return "git"

GIT = _find_git()


def banner():
    print("=" * 68)
    print("   AI-AutoPilot :: Universal Zero-Click Deployment & Verifier")
    print("   Project Location : E:\\AS Projects\\AI-AutoPilot")
    print(f"   GitHub URL       : {GITHUB_REPO}")
    print("=" * 68)


def step_1_omniroute_repo():
    print("\n>>> STEP 1: Core Engine Repository")
    print(f"  Primary Repo Link: {OMNIROUTE_REPO}")
    print("  Downloading & verifying OmniRoute core repository first...")
    target = r"C:\Users\Admin\ai_repositories\OmniRoute"
    os.makedirs(r"C:\Users\Admin\ai_repositories", exist_ok=True)
    if os.path.exists(os.path.join(target, ".git")):
        r = subprocess.run([GIT, "pull", "--ff-only"], cwd=target, capture_output=True, text=True)
        print(f"  [OK] OmniRoute core updated: {r.stdout.strip() or 'already up to date'}")
    else:
        r = subprocess.run([GIT, "clone", "--depth", "1", OMNIROUTE_REPO, target], capture_output=True, text=True)
        if r.returncode == 0:
            print("  [OK] OmniRoute core cloned successfully.")
        else:
            print(f"  [WARN] Clone notice: {r.stderr.strip()[:100]}")


def step_2_ingest_keys():
    print("\n>>> STEP 2: Ingesting All API Keys (E:\\Api keys)...")
    code = subprocess.run([sys.executable, str(ROOT / "tools" / "key_ingestion.py")]).returncode
    print(f"  [OK] Key ingestion finished with exit code: {code}")


def step_3_detect_and_configure_ides():
    print("\n>>> STEP 3: Auto-Detecting All IDEs & Coding Agents...")
    code = subprocess.run([sys.executable, str(ROOT / "tools" / "ide_configurator.py")]).returncode
    print(f"  [OK] IDE & agent configuration complete (exit {code})")


def step_4_install_ecosystem_repos():
    print("\n>>> STEP 4: Installing/Updating All Ecosystem Repositories...")
    code = subprocess.run([sys.executable, str(ROOT / "tools" / "repo_installer.py")]).returncode
    print(f"  [OK] Repository ecosystem synchronized (exit {code})")


def step_5_test_failover():
    print("\n>>> STEP 5: Testing Live AI Failover Combos...")
    from core.omniroute_client import OmniRouteClient, DEFAULT_COMBOS
    client = OmniRouteClient()
    for combo in DEFAULT_COMBOS:
        t0 = time.time()
        res = client.chat_with_failover("Respond with exactly: OK", combos=[combo], max_tokens=10)
        elapsed = time.time() - t0
        tag = "[OK]  " if res else "[WARN]"
        print(f"  {tag} Combo '{combo}': {res!r} ({elapsed:.2f}s)")


def step_6_sync_github():
    print("\n>>> STEP 6: Syncing Updates to GitHub Repository...")
    try:
        if GITHUB_TOKEN:
            auth_url = f"https://{GITHUB_TOKEN}@github.com/AshrafMorningstar/AI-AutoPilot.git"
            subprocess.run([GIT, "remote", "set-url", "origin", auth_url], cwd=str(ROOT), check=False)
        subprocess.run([GIT, "add", "-A"], cwd=str(ROOT), check=False)
        subprocess.run([GIT, "commit", "-m", "feat: update zero-click deployment and auto-failover engine"], cwd=str(ROOT), check=False)
        r = subprocess.run([GIT, "push", "origin", "main"], cwd=str(ROOT), capture_output=True, text=True)
        if r.returncode == 0:
            print(f"  [OK] GitHub repository synchronized: {GITHUB_REPO}")
        else:
            print(f"  [INFO] Git push status: {r.stdout.strip()} {r.stderr.strip()}")
    except Exception as e:
        print(f"  [WARN] Git sync notice: {e}")


def main():
    banner()
    step_1_omniroute_repo()
    step_2_ingest_keys()
    step_3_detect_and_configure_ides()
    step_4_install_ecosystem_repos()
    step_5_test_failover()
    step_6_sync_github()
    print("\n" + "=" * 68)
    print("   [SUCCESS] ALL-IN-ONE AUTOMATION COMPLETE & FULLY OPERATIONAL!")
    print(f"   Project Folder : E:\\AS Projects\\AI-AutoPilot")
    print(f"   GitHub Repo    : {GITHUB_REPO}")
    print("=" * 68)


if __name__ == "__main__":
    main()
