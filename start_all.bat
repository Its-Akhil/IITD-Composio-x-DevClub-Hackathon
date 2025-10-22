@echo off
echo ============================================
echo    AI Social Factory - Complete Startup
echo ============================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then: venv\Scripts\activate.bat
    echo Then: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [2/3] Starting Backend Server (FastAPI)...
echo Backend will run at: http://localhost:8000
start "AI Social Factory - Backend" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait for backend to start
timeout /t 3 /nobreak > nul

echo.
echo [3/3] Starting Frontend Server...
echo Frontend will run at: http://localhost:3000
start "AI Social Factory - Frontend" cmd /k "python start_frontend.py"

echo.
echo ============================================
echo    Servers Starting...
echo ============================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Browser will open automatically in a few seconds...
echo.
echo Press any key to stop all servers...
pause > nul

echo.
echo Shutting down servers...
taskkill /FI "WindowTitle eq AI Social Factory - Backend*" /T /F 2>nul
taskkill /FI "WindowTitle eq AI Social Factory - Frontend*" /T /F 2>nul
echo.
echo Servers stopped. Goodbye!
