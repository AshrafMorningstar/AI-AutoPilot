@echo off
:: AI-AutoPilot :: One-Click Zero-Click Installer
:: Runs FULL automated setup: API keys + IDEs + Repos + Health Test
:: No Python environment needed — uses system Python

echo.
echo ================================================================
echo   AI-AutoPilot : Zero-Click Full Automated Setup
echo   Configures: OmniRoute + All IDEs + All AI Tools + All Repos
echo ================================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

:: Set default environment
set OMNIROUTE_URL=http://127.0.0.1:20128
set OMNIROUTE_KEY=sk-3a0b09e07366b474-63292a-294d391c
set OPENAI_API_KEY=sk-3a0b09e07366b474-358946-ff6459d4

:: Run master setup
cd /d "%~dp0"
python autopilot.py setup

echo.
echo ================================================================
echo   Setup complete! Use the following commands:
echo   python autopilot.py status     -- Check gateway
echo   python autopilot.py run "..."  -- Run AI prompt
echo   python autopilot.py wrap cmd   -- Supervise agent
echo ================================================================
echo.
pause
