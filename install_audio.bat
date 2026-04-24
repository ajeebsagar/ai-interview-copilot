@echo off
REM Install Audio Transcription (Faster Whisper)
REM This script installs faster-whisper for real audio transcription

echo ========================================
echo Install Audio Transcription
echo ========================================
echo.

echo This will install:
echo   - faster-whisper (Python package)
echo   - All required dependencies
echo   - Whisper model (downloaded on first use)
echo.

set /p CONFIRM="Do you want to proceed? (Y/N): "

if /i "%CONFIRM%" NEQ "Y" (
    echo Installation cancelled.
    pause
    exit /b 0
)

echo.
echo Step 1: Activating virtual environment...
cd backend
call venv\Scripts\activate.bat

echo.
echo Step 2: Installing faster-whisper...
pip install faster-whisper

echo.
echo Step 3: Verifying installation...
pip list | findstr faster-whisper

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Audio transcription installed
    echo ========================================
    echo.
    echo Next steps:
    echo   1. Restart your backend server (Ctrl+C, then restart)
    echo   2. Try recording audio in the extension
    echo   3. You should see real transcription (not MOCK)
    echo.
    echo Note: First use will download the model (~150MB)
    echo       This takes 30-60 seconds, then it's fast!
    echo.
) else (
    echo.
    echo ========================================
    echo ERROR: Installation may have failed
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo You can try manual installation:
    echo   cd backend
    echo   venv\Scripts\activate
    echo   pip install faster-whisper
    echo.
)

pause
