@echo off
:: AI-AutoPilot GitHub Publisher
:: ================================
:: Run this file to push AI-AutoPilot to GitHub automatically.
:: 
:: STEP 1: Get a GitHub token:
::   1. Open: https://github.com/settings/tokens/new
::   2. Note: "AI-AutoPilot"
::   3. Expiration: 90 days
::   4. Scopes: Check "repo" and "workflow"
::   5. Click "Generate token" and copy it
::
:: STEP 2: Set your token below, then double-click this file.

set GITHUB_TOKEN=PASTE_YOUR_TOKEN_HERE
set GITHUB_USERNAME=PASTE_YOUR_GITHUB_USERNAME_HERE

:: ── Do not edit below this line ──────────────────────────────
if "%GITHUB_TOKEN%"=="PASTE_YOUR_TOKEN_HERE" (
    echo [ERROR] Please edit this file and set your GitHub token first!
    echo Open PUSH_TO_GITHUB.bat with Notepad and fill in the token.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo   AI-AutoPilot :: Pushing to GitHub
echo ================================================================
echo.

cd /d "%~dp0"

:: Install dependencies and run publisher
python scripts\publish_github.py --token "%GITHUB_TOKEN%" --username "%GITHUB_USERNAME%"

pause
