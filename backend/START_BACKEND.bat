@echo off
echo ========================================
echo Starting LockedIn AI Backend Server
echo ========================================
echo.

cd /d "%~dp0"

echo Cleaning Python cache...
rmdir /s /q src\__pycache__ 2>nul
rmdir /s /q src\api\__pycache__ 2>nul
rmdir /s /q src\services\__pycache__ 2>nul
rmdir /s /q src\models\__pycache__ 2>nul
rmdir /s /q src\middleware\__pycache__ 2>nul
rmdir /s /q src\config\__pycache__ 2>nul
rmdir /s /q src\utils\__pycache__ 2>nul
del /f /q src\*.pyc 2>nul
del /f /q src\*\*.pyc 2>nul
echo Cache cleaned.
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting server on http://localhost:8000
echo Press Ctrl+C to stop
echo.
echo API Docs: http://localhost:8000/docs
echo Health: http://localhost:8000/api/v1/health
echo.

python -m src.main

pause
