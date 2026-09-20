@echo off
:: ============================================================================
:: AI-AutoPilot :: Zero-Click Master Launcher
:: Automatically configures all IDEs, downloads OmniRoute & all repos,
:: ingests API keys, tests failover live, and syncs to GitHub!
:: ============================================================================
setlocal
cd /d "%~dp0"

echo [*] Starting AI-AutoPilot Master Zero-Click Deployment...
python scripts\auto_detect_and_deploy.py

echo.
pause
