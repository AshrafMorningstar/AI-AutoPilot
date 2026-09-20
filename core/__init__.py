# AI-AutoPilot core package
from .omniroute_client import OmniRouteClient, get_client, FAILOVER_SIGNALS, DEFAULT_COMBOS
from .failover_supervisor import supervise

__all__ = ["OmniRouteClient", "get_client", "FAILOVER_SIGNALS", "DEFAULT_COMBOS", "supervise"]
