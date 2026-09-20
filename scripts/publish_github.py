#!/usr/bin/env python3
"""
AI-AutoPilot :: GitHub Publisher
==================================
Creates the GitHub repository and pushes all code automatically.
Run: python scripts/publish_github.py --token YOUR_GITHUB_PAT_TOKEN

Get a token at: https://github.com/settings/tokens/new
Required scope: repo, workflow
"""

import sys
import os
import json
import subprocess
import urllib.request
import urllib.error
import argparse


REPO_NAME        = "AI-AutoPilot"
REPO_DESCRIPTION = "Zero-Click AI Agent AutoPilot: Automatic failover across Claude, GPT-4, Gemini, Groq & 15+ providers. Configures ALL IDEs & coding agents automatically. Never hit a rate limit again."
REPO_TOPICS      = [
    "ai", "llm", "autopilot", "omniroute", "failover",
    "claude", "openai", "gemini", "groq", "gpt4",
    "coding-agent", "vscode", "cursor", "automation",
    "ai-tools", "rate-limit", "multi-provider", "python",
    "claude-code", "aider"
]
GITHUB_API = "https://api.github.com"


def api_call(token: str, method: str, path: str, data: dict = None):
    url = f"{GITHUB_API}{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "AI-AutoPilot/1.0",
    }
    body = json.dumps(data).encode() if data else None
    req  = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body
    except Exception as e:
        return 500, str(e)


def main():
    parser = argparse.ArgumentParser(description="Publish AI-AutoPilot to GitHub")
    parser.add_argument("--token", required=True, help="GitHub Personal Access Token (repo + workflow scopes)")
    parser.add_argument("--private", action="store_true", help="Create as private repo (default: public)")
    parser.add_argument("--username", help="GitHub username (auto-detected if not specified)")
    args = parser.parse_args()

    token = args.token

    # ── 1. Get authenticated user ──────────────────────────────────────────
    print("[1/5] Authenticating with GitHub...")
    code, user = api_call(token, "GET", "/user")
    if code != 200:
        print(f"[ERROR] GitHub auth failed (HTTP {code}): {user}")
        sys.exit(1)
    username = args.username or user.get("login", "")
    print(f"  Logged in as: {username}")

    # ── 2. Create repository ───────────────────────────────────────────────
    print(f"\n[2/5] Creating repo '{REPO_NAME}'...")
    code, resp = api_call(token, "POST", "/user/repos", {
        "name":        REPO_NAME,
        "description": REPO_DESCRIPTION,
        "private":     args.private,
        "auto_init":   False,
        "has_issues":  True,
        "has_wiki":    False,
    })
    if code == 201:
        clone_url = resp.get("html_url", f"https://github.com/{username}/{REPO_NAME}")
        print(f"  Created: {clone_url}")
    elif code == 422 and "already exists" in str(resp).lower():
        print(f"  Repo already exists — using existing.")
        clone_url = f"https://github.com/{username}/{REPO_NAME}"
    else:
        print(f"  [WARN] Repo creation HTTP {code}: {resp}")
        clone_url = f"https://github.com/{username}/{REPO_NAME}"

    # ── 3. Add repository topics ───────────────────────────────────────────
    print(f"\n[3/5] Setting SEO topics...")
    code, resp = api_call(
        token, "PUT",
        f"/repos/{username}/{REPO_NAME}/topics",
        {"names": REPO_TOPICS}
    )
    if code in (200, 201, 204):
        print(f"  Topics set: {', '.join(REPO_TOPICS[:8])}... and {len(REPO_TOPICS)-8} more")
    else:
        print(f"  [WARN] Topics HTTP {code}: {resp}")

    # ── 4. Set remote and push ─────────────────────────────────────────────
    print(f"\n[4/5] Pushing code to GitHub...")
    remote_url = f"https://{token}@github.com/{username}/{REPO_NAME}.git"

    # Set or update remote
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def git(args_list):
        return subprocess.run(
            ["git"] + args_list,
            cwd=project_root,
            capture_output=True,
            text=True,
        )

    # Remove existing remote if any
    git(["remote", "remove", "origin"])
    result = git(["remote", "add", "origin", remote_url])

    # Push main branch
    result = git(["push", "-u", "origin", "main", "--force"])
    if result.returncode == 0:
        print(f"  Pushed successfully!")
    else:
        print(f"  [WARN] Push stderr: {result.stderr[:200]}")
        # Try master if main failed
        result2 = git(["push", "-u", "origin", "master:main", "--force"])
        if result2.returncode == 0:
            print(f"  Pushed (master->main) successfully!")

    # ── 5. Final summary ───────────────────────────────────────────────────
    print(f"\n[5/5] Done!")
    print("=" * 60)
    print(f"  GitHub URL : https://github.com/{username}/{REPO_NAME}")
    print(f"  Stars      : 0 (fresh!)")
    print(f"  Topics     : {len(REPO_TOPICS)} SEO tags added")
    print()
    print("  Next steps to go viral:")
    print("  1. Add a great screenshot to docs/ and link it in README.md")
    print("  2. Post on Reddit: r/LocalLLaMA, r/ChatGPT, r/programming")
    print("  3. Post on Hacker News: Show HN: AI-AutoPilot")
    print("  4. Post on X (Twitter) with hashtags: #AI #LLM #Claude #OpenAI")
    print("  5. Submit to Product Hunt, dev.to, Medium")
    print("=" * 60)


if __name__ == "__main__":
    main()
