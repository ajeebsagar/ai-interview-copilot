@echo off
REM LockedIn AI - Comprehensive Testing Script
REM Starts backend and runs all tests

echo ========================================
echo LockedIn AI - Comprehensive Test Runner
echo ========================================
echo.

echo Step 1: Checking Python environment...
cd backend
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat

echo Step 3: Checking backend server...
curl -s http://localhost:8000/api/v1/health >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Backend not running. Starting server...
    echo.
    echo Starting backend server in background...
    start "LockedIn Backend" cmd /c "venv\Scripts\activate.bat && python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"

    echo Waiting for server to start...
    timeout /t 5 /nobreak >nul

    REM Wait for server to be ready
    :wait_loop
    curl -s http://localhost:8000/api/v1/health >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo Still waiting for server...
        timeout /t 2 /nobreak >nul
        goto wait_loop
    )

    echo ✅ Server started successfully!
) else (
    echo ✅ Server already running!
)

echo.
echo Step 4: Running comprehensive test suite...
echo.
cd ..
python comprehensive_test_suite.py

echo.
echo ========================================
echo Step 5: Test Results
echo ========================================
if exist test_results.json (
    echo Test results saved to: test_results.json
    type test_results.json
) else (
    echo No test results file found
)

echo.
echo ========================================
echo All tests completed!
echo ========================================
pause
