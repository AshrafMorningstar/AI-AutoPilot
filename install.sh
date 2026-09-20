#!/usr/bin/env bash
# AI-AutoPilot :: Zero-Click Unix/macOS/WSL Installer
set -e

echo ""
echo "================================================================"
echo "  AI-AutoPilot : Zero-Click Full Automated Setup"
echo "================================================================"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] python3 not found. Install Python 3.8+ first."
    exit 1
fi

export OMNIROUTE_URL="http://127.0.0.1:20128"
export OMNIROUTE_KEY="sk-3a0b09e07366b474-63292a-294d391c"
export OPENAI_API_KEY="sk-3a0b09e07366b474-358946-ff6459d4"

cd "$(dirname "$0")"
python3 autopilot.py setup

echo ""
echo "================================================================"
echo "  Setup complete!"
echo "  python3 autopilot.py status     -- Check gateway"
echo "  python3 autopilot.py run '...'  -- Run AI prompt"
echo "  python3 autopilot.py wrap cmd   -- Supervise agent"
echo "================================================================"
