@echo off
REM Azure OpenAI Configuration Update Script
REM Updates .env file with correct deployment name and API version

echo ========================================
echo Azure OpenAI Configuration Update
echo ========================================
echo.

cd backend

echo Current configuration:
echo.
findstr /C:"AZURE_OPENAI_DEPLOYMENT_NAME" .env
findstr /C:"AZURE_OPENAI_API_VERSION" .env
findstr /C:"AZURE_OPENAI_ENDPOINT" .env
echo.

echo ========================================
echo IMPORTANT: Update Instructions
echo ========================================
echo.
echo 1. Your API key may have expired (401 error)
echo 2. You want to change deployment from gpt-4.1-mini to gpt-5-nano
echo.
echo To fix:
echo   Option A - Manual Edit (Recommended):
echo     1. Open backend\.env in notepad
echo     2. Update these lines:
echo        AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5-nano
echo        AZURE_OPENAI_API_VERSION=2024-10-21
echo     3. Get new API key from Azure Portal if needed
echo.
echo   Option B - Automatic Update (this script):
echo.

set /p CONFIRM="Do you want this script to update .env automatically? (Y/N): "

if /i "%CONFIRM%" NEQ "Y" (
    echo.
    echo Update cancelled. Please edit backend\.env manually.
    echo.
    pause
    exit /b 0
)

echo.
echo Updating .env file...

REM Create backup
copy .env .env.backup >nul
echo Backup created: .env.backup

REM Update deployment name
powershell -Command "(Get-Content .env) -replace 'AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4\.1-mini', 'AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5-nano' | Set-Content .env"
echo Updated: AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5-nano

REM Update API version to stable version
powershell -Command "(Get-Content .env) -replace 'AZURE_OPENAI_API_VERSION=2024-12-01-preview', 'AZURE_OPENAI_API_VERSION=2024-10-21' | Set-Content .env"
echo Updated: AZURE_OPENAI_API_VERSION=2024-10-21

echo.
echo ========================================
echo Configuration Updated!
echo ========================================
echo.
echo New configuration:
echo.
findstr /C:"AZURE_OPENAI_DEPLOYMENT_NAME" .env
findstr /C:"AZURE_OPENAI_API_VERSION" .env
echo.

echo NEXT STEPS:
echo.
echo 1. Check if deployment 'gpt-5-nano' exists in Azure:
echo    - Go to: https://oai.azure.com
echo    - Check Deployments section
echo.
echo 2. If you see 401 errors, update your API key:
echo    - Go to: https://portal.azure.com
echo    - Find your Azure OpenAI resource
echo    - Go to 'Keys and Endpoint'
echo    - Copy KEY 1 or KEY 2
echo    - Update AZURE_OPENAI_API_KEY in .env
echo.
echo 3. Restart your backend server for changes to take effect
echo.

pause
