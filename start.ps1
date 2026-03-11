# AI-PMS Quick Start Script
# Starts both backend and frontend servers

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  AI-PMS v2.0 - Intelligent Dashboard Starter" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js detected: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found! Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Starting servers..." -ForegroundColor Yellow
Write-Host ""

# Start Backend Server
Write-Host "→ Starting Backend API (Port 8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
    Write-Host '========================================' -ForegroundColor Magenta
    Write-Host '  BACKEND SERVER (FastAPI)' -ForegroundColor Magenta
    Write-Host '  Port: 8000' -ForegroundColor Magenta
    Write-Host '========================================' -ForegroundColor Magenta
    Write-Host ''
    cd '$PSScriptRoot\backend'
    python app.py
"@

Start-Sleep -Seconds 3

# Start Frontend Server
Write-Host "→ Starting Frontend (Port 3000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
    Write-Host '========================================' -ForegroundColor Magenta
    Write-Host '  FRONTEND SERVER (React + Vite)' -ForegroundColor Magenta
    Write-Host '  Port: 3000' -ForegroundColor Magenta
    Write-Host '========================================' -ForegroundColor Magenta
    Write-Host ''
    cd '$PSScriptRoot\frontend'
    npm run dev
"@

Start-Sleep -Seconds 5

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  ✓ Both servers are starting!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor Yellow
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in server windows to stop" -ForegroundColor Gray
Write-Host ""
Write-Host "Enjoy your AI-Powered Dashboard! 🚀" -ForegroundColor Cyan
