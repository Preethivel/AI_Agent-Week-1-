@echo off
echo ============================================================
echo 🤖 AI AGENT - REACT + OLLAMA
echo ============================================================
echo.
echo Starting Backend Server...
start cmd /k "cd backend && python app.py"

echo.
echo Starting React Frontend...
start cmd /k "cd frontend && npm start"

echo.
echo ============================================================
echo ✅ Both servers are starting...
echo 📍 Backend: http://127.0.0.1:5001
echo 📍 Frontend: http://127.0.0.1:3000
echo ============================================================