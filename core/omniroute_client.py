#!/usr/bin/env python3
"""
AI-AutoPilot :: OmniRoute Client Core
======================================
Full-featured OmniRoute gateway client with:
- Automatic failover across any provider/model
- Real-time rate-limit detection
- Health monitoring and metrics
- Key registration and combo management
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from typing import Optional, List, Dict, Tuple, Any

# ── Gateway Configuration ────────────────────────────────────────────────────
OMNIROUTE_URL   = os.environ.get("OMNIROUTE_URL",  "http://127.0.0.1:20128")
ADMIN_KEY       = os.environ.get("OMNIROUTE_KEY",  "sk-3a0b09e07366b474-63292a-294d391c")
INFERENCE_KEY   = os.environ.get("OPENAI_API_KEY", "sk-3a0b09e07366b474-358946-ff6459d4")

# ── Failover Signal Keywords ─────────────────────────────────────────────────
FAILOVER_SIGNALS = [
    "429", "rate limit", "quota", "overloaded", "resource_exhausted",
    "exceeded your current quota", "insufficient_quota",
    "socket hang up", "forcibly closed by the remote host",
    "502 bad gateway", "503 service unavailable",
    "connection reset", "timed out", "ssl error",
    "context_length_exceeded", "model_not_available",
]

# ── Default Failover Combos ──────────────────────────────────────────────────
DEFAULT_COMBOS = ["Coding Failover", "Fast Auto Failover"]


class OmniRouteClient:
    """Full OmniRoute programmatic client."""

    def __init__(
        self,
        base_url: str = OMNIROUTE_URL,
        admin_key: str = ADMIN_KEY,
        inference_key: str = INFERENCE_KEY,
        timeout: int = 30,
    ):
        self.base_url      = base_url.rstrip("/")
        self.admin_key     = admin_key
        self.inference_key = inference_key
        self.timeout       = timeout

    # ── Internal HTTP helper ─────────────────────────────────────────────────
    def _request(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict] = None,
        use_admin: bool = True,
    ) -> Tuple[int, Any]:
        url     = f"{self.base_url}{endpoint}"
        key     = self.admin_key if use_admin else self.inference_key
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type":  "application/json",
        }
        encoded = json.dumps(data).encode("utf-8") if data is not None else None
        req     = urllib.request.Request(url, data=encoded, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
                try:
                    return resp.status, json.loads(raw)
                except Exception:
                    return resp.status, raw
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            try:
                return e.code, json.loads(body)
            except Exception:
                return e.code, body
        except Exception as e:
            return 500, {"error": str(e)}

    # ── Health & Status ──────────────────────────────────────────────────────
    def get_health(self) -> Tuple[int, Any]:
        return self._request("/api/health")

    def is_online(self) -> bool:
        code, _ = self.get_health()
        return code == 200

    # ── Providers ────────────────────────────────────────────────────────────
    def list_providers(self) -> Tuple[int, Any]:
        return self._request("/api/providers")

    def register_key(
        self,
        provider: str,
        name: str,
        api_key: str,
        priority: int = 1,
    ) -> Tuple[int, Any]:
        return self._request(
            "/api/providers",
            method="POST",
            data={"provider": provider, "name": name, "apiKey": api_key, "priority": priority},
        )

    # ── Combos ───────────────────────────────────────────────────────────────
    def list_combos(self) -> Tuple[int, Any]:
        return self._request("/api/combos")

    def create_combo(
        self,
        name: str,
        models: List[str],
        strategy: str = "priority",
    ) -> Tuple[int, Any]:
        return self._request(
            "/api/combos",
            method="POST",
            data={"name": name, "strategy": strategy, "models": models},
        )

    def update_combo(
        self,
        combo_id: str,
        name: str,
        models: List[str],
        strategy: str = "priority",
    ) -> Tuple[int, Any]:
        return self._request(
            f"/api/combos/{combo_id}",
            method="PUT",
            data={"id": combo_id, "name": name, "strategy": strategy, "models": models},
        )

    # ── Inference ────────────────────────────────────────────────────────────
    def chat(
        self,
        model: str,
        messages: List[Dict],
        max_tokens: int = 1024,
        stream: bool = False,
    ) -> Tuple[int, Any]:
        return self._request(
            "/v1/chat/completions",
            method="POST",
            data={"model": model, "messages": messages, "max_tokens": max_tokens, "stream": stream},
            use_admin=False,
        )

    def chat_with_failover(
        self,
        prompt: str,
        combos: Optional[List[str]] = None,
        max_tokens: int = 1024,
    ) -> Optional[str]:
        """
        Send a prompt with automatic failover across all configured combos.
        Returns the first successful response content, or None if all fail.
        """
        routes = list(combos or DEFAULT_COMBOS) + ["gpt-4o-mini", "gemini-2.5-flash"]
        messages = [
            {"role": "system", "content": "You are a powerful AI assistant."},
            {"role": "user",   "content": prompt},
        ]
        for idx, model in enumerate(routes):
            if idx > 0:
                print(f"[OmniRoute] [FAILOVER] -> switching to '{model}'", flush=True)
            try:
                code, resp = self.chat(model, messages, max_tokens=max_tokens)
                if code == 200 and "choices" in resp:
                    return resp["choices"][0]["message"]["content"]
                err_str = str(resp).lower()
                if any(s in err_str for s in FAILOVER_SIGNALS):
                    print(f"[OmniRoute] Rate-limit signal detected on '{model}'. Failing over...", flush=True)
                    continue
                print(f"[OmniRoute] '{model}' returned HTTP {code}: {str(resp)[:120]}", flush=True)
            except Exception as e:
                print(f"[OmniRoute] '{model}' error: {e}", flush=True)
        return None

    # ── Routing strategy ─────────────────────────────────────────────────────
    def set_strategy(self, strategy: str) -> Tuple[int, Any]:
        return self._request("/api/routing-strategy", method="POST", data={"strategy": strategy})

    def set_resilience(self, profile: str) -> Tuple[int, Any]:
        return self._request("/api/resilience", method="POST", data={"profile": profile})


# ── Singleton helper ─────────────────────────────────────────────────────────
_client: Optional[OmniRouteClient] = None


def get_client() -> OmniRouteClient:
    global _client
    if _client is None:
        _client = OmniRouteClient()
    return _client


if __name__ == "__main__":
    c = get_client()
    ok, data = c.get_health()
    print(f"Gateway Health: HTTP {ok}")
    print(json.dumps(data, indent=2) if isinstance(data, dict) else data)
