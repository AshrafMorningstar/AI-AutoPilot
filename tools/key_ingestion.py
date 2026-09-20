#!/usr/bin/env python3
"""
AI-AutoPilot :: API Key Ingestion Tool
========================================
Reads all API keys from E:\\Api keys (and other configured paths),
detects the provider for each key, and registers it in OmniRoute.

Supported providers (auto-detected by key prefix):
  sk-ant-*         → Anthropic (Claude)
  sk-*             → OpenAI / OmniRoute
  gsk_*            → Groq
  AIza*            → Google Gemini
  nvapi-*          → NVIDIA NIM
  xai-*            → xAI / Grok
  r8_*             → Replicate
  hf_*             → HuggingFace
  or-*             → OpenRouter
  claude-*         → Anthropic (legacy)
"""

import os
import re
import sys
import json
import time
import urllib.request
import urllib.error
from typing import List, Tuple, Optional

# ── Gateway config ─────────────────────────────────────────────────────────
OMNIROUTE_URL = os.environ.get("OMNIROUTE_URL", "http://127.0.0.1:20128")
ADMIN_KEY     = os.environ.get("OMNIROUTE_KEY", "sk-3a0b09e07366b474-63292a-294d391c")

# ── Key source directories ─────────────────────────────────────────────────
KEY_DIRS = [
    r"E:\Api keys",
    r"C:\Users\Admin\api_keys",
    r"C:\Users\Admin\.config\api_keys",
]

# ── Provider detection rules ────────────────────────────────────────────────
PROVIDER_RULES = [
    (r"^sk-ant-",       "anthropic"),
    (r"^AIza",          "gemini"),
    (r"^gsk_",          "groq"),
    (r"^nvapi-",        "nvidia"),
    (r"^xai-",          "xai"),
    (r"^r8_",           "replicate"),
    (r"^hf_",           "huggingface"),
    (r"^or-",           "openrouter"),
    (r"^claude-",       "anthropic"),
    (r"^sk-3a0b09e",    "omniroute"),  # OmniRoute native keys
    (r"^sk-",           "openai"),
]

# Regex to extract candidates from arbitrary text files
KEY_RE = re.compile(
    r"\b(sk-ant-[A-Za-z0-9\-_]{20,}|AIza[A-Za-z0-9\-_]{30,}|gsk_[A-Za-z0-9]{30,}"
    r"|nvapi-[A-Za-z0-9\-_]{20,}|xai-[A-Za-z0-9]{20,}|r8_[A-Za-z0-9]{30,}"
    r"|hf_[A-Za-z0-9]{20,}|or-[A-Za-z0-9]{30,}|sk-[A-Za-z0-9\-_]{20,})\b"
)


def detect_provider(key: str) -> Optional[str]:
    for pattern, provider in PROVIDER_RULES:
        if re.match(pattern, key):
            return provider
    return None


def scan_directory(directory: str) -> List[Tuple[str, str]]:
    """
    Scan all text files in directory and return list of (key, provider) tuples.
    """
    results: List[Tuple[str, str]] = []
    if not os.path.isdir(directory):
        return results

    for fname in os.listdir(directory):
        fpath = os.path.join(directory, fname)
        if not os.path.isfile(fpath):
            continue
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            for match in KEY_RE.finditer(content):
                key = match.group(0)
                provider = detect_provider(key)
                if provider:
                    results.append((key, provider))
        except Exception:
            pass
    return results


def register_key(key: str, provider: str, name: str, priority: int = 1) -> Tuple[int, dict]:
    url     = f"{OMNIROUTE_URL}/api/providers"
    payload = json.dumps({
        "provider": provider,
        "name":     name,
        "apiKey":   key,
        "priority": priority,
    }).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {ADMIN_KEY}",
        "Content-Type":  "application/json",
    }
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(body)
            except Exception:
                return resp.status, {"raw": body}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        return e.code, {"error": body[:200]}
    except Exception as e:
        return 500, {"error": str(e)}


def main():
    print("=" * 60)
    print("   AI-AutoPilot :: API Key Ingestion Tool")
    print("=" * 60)

    # Collect all keys
    all_keys: List[Tuple[str, str]] = []
    for d in KEY_DIRS:
        found = scan_directory(d)
        if found:
            print(f"  [DIR] {d}: found {len(found)} key(s)")
            all_keys.extend(found)

    # Deduplicate
    seen = set()
    unique_keys: List[Tuple[str, str]] = []
    for key, provider in all_keys:
        if key not in seen:
            seen.add(key)
            unique_keys.append((key, provider))

    print(f"\n  Total unique keys found : {len(unique_keys)}")
    if not unique_keys:
        print("  [WARN]  No keys found. Check your E:\\Api keys directory.")
        return

    # Group by provider for a nice summary
    by_provider: dict = {}
    for key, provider in unique_keys:
        by_provider.setdefault(provider, []).append(key)
    for p, keys in sorted(by_provider.items()):
        print(f"  {p:<15} : {len(keys)} key(s)")

    print("\n  Registering all keys in OmniRoute...\n")
    ok = fail = skip = 0
    for idx, (key, provider) in enumerate(unique_keys, 1):
        # Skip OmniRoute's own admin/inference keys (already built in)
        if key.startswith("sk-3a0b09e"):
            skip += 1
            continue
        name   = f"{provider.title()} Key #{idx}"
        code, resp = register_key(key, provider, name)
        icon   = "[OK]" if code in (200, 201) else "[WARN] "
        detail = key[:12] + "..."
        msg    = resp.get("error", resp.get("id", str(resp)))[:60] if isinstance(resp, dict) else str(resp)[:60]
        print(f"  {icon} [{code}] {provider:<14} {detail}  {msg}")
        if code in (200, 201):
            ok += 1
        else:
            fail += 1
        time.sleep(0.1)

    print("\n" + "=" * 60)
    print(f"  [OK] {ok} registered  |  [FAIL] {fail} failed  |  [SKIP] {skip} skipped")
    print("=" * 60)


if __name__ == "__main__":
    main()
