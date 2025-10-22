# Start Development Server (with auto-reload, excluding certain folders)
# This prevents the server from restarting when videos, logs, or model files change

Write-Host "Starting AI Social Factory - Development Mode" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Auto-reload is ENABLED for code changes" -ForegroundColor Green
Write-Host "Auto-reload is DISABLED for:" -ForegroundColor Yellow
Write-Host "  - generated_videos/ folder" -ForegroundColor Yellow
Write-Host "  - logs/ folder" -ForegroundColor Yellow
Write-Host "  - local_t2v_model/ folder" -ForegroundColor Yellow
Write-Host "  - Database files (*.db)" -ForegroundColor Yellow
Write-Host "  - Video files (*.mp4)" -ForegroundColor Yellow
Write-Host "  - Log files (*.log)" -ForegroundColor Yellow
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

# Start uvicorn with reload excludes
uvicorn app.main:app `
    --host 0.0.0.0 `
    --port 8000 `
    --reload `
    --reload-exclude "generated_videos/*" `
    --reload-exclude "logs/*" `
    --reload-exclude "*.log" `
    --reload-exclude "*.mp4" `
    --reload-exclude "*.db" `
    --reload-exclude "*.db-journal" `
    --reload-exclude "__pycache__/*" `
    --reload-exclude ".git/*" `
    --reload-exclude "venv/*" `
    --reload-exclude "local_t2v_model/*" `
    --reload-exclude ".pytest_cache/*"
