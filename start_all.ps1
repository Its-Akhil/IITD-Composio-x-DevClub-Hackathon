# AI Social Factory - Complete Startup Script
# Starts both backend and frontend servers

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   AI Social Factory - Complete Startup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv"
    Write-Host "Then: .\venv\Scripts\Activate.ps1"
    Write-Host "Then: pip install -r requirements.txt"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[1/3] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "[2/3] Starting Backend Server (FastAPI)..." -ForegroundColor Yellow
Write-Host "Backend will run at: http://localhost:8000" -ForegroundColor Green

# Start backend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '.\venv\Scripts\Activate.ps1'; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Normal

# Wait for backend to start
Write-Host "Waiting for backend to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "[3/3] Starting Frontend Server..." -ForegroundColor Yellow
Write-Host "Frontend will run at: http://localhost:3000" -ForegroundColor Green

# Start frontend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '.\venv\Scripts\Activate.ps1'; python start_frontend.py" -WindowStyle Normal

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "    Servers Starting..." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Browser will open automatically in a few seconds..." -ForegroundColor Yellow
Write-Host ""
Write-Host "To stop servers: Close the backend and frontend windows" -ForegroundColor Gray
Write-Host ""

# Wait a bit more then open browser
Start-Sleep -Seconds 2
Start-Process "http://localhost:3000/index.html"

Write-Host "Press Enter to exit this window (servers will keep running)..." -ForegroundColor Cyan
Read-Host
