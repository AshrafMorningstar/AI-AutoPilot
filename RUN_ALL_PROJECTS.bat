@echo off
:: ============================================================================
:: AI-AutoPilot :: Run & Verify All 21 Projects in 1 Click
:: ============================================================================
setlocal
cd /d "%~dp0"

echo [*] Launching AI-AutoPilot Universal Project Orchestrator...
python core\ecosystem_runner.py

echo.
pause
