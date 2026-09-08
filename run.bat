@echo off
echo =======================================================
echo Starting AI Batch Quality Evaluation System...
echo =======================================================

echo 1. Starting Backend (FastAPI on Port 8000)...
start "Backend Server" cmd /k "cd /d x:\manufactoring && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

echo 2. Starting Frontend (React/Vite on Port 5173)...
start "Frontend Server" cmd /k "cd /d x:\manufactoring\frontend && npm run dev"

echo 3. Starting Ollama Server...
start "Ollama Server" cmd /k "ollama serve"

echo.
echo Both servers are starting in separate windows!
echo Once they are ready, open your browser to: http://localhost:5173
echo =======================================================
