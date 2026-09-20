@echo off
:: ============================================================================
:: AI-AutoPilot :: Test & Upload to Both GitHub Repositories
:: ============================================================================
setlocal
cd /d "%~dp0"

echo [*] Testing system and uploading to both GitHub repositories...
python scripts\upload_to_both_repos.py

echo.
pause
