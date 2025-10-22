# Start Production Server (no auto-reload)
# Use this for production deployment or when you don't want any auto-reload

Write-Host "Starting AI Social Factory - Production Mode" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Auto-reload is DISABLED" -ForegroundColor Red
Write-Host "Server will NOT restart on file changes" -ForegroundColor Yellow
Write-Host ""
Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "API documentation: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment if not already active
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
}

# Start uvicorn without reload
uvicorn app.main:app `
    --host 0.0.0.0 `
    --port 8000
