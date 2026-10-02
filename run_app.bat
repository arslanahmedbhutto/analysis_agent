@echo off
title InsightAgent AI - Autonomous Data Analyst
echo =========================================================
echo       InsightAgent AI - Autonomous Data Analysis Suite
echo =========================================================
echo.

:: Check if Ollama is installed and running
echo [1/2] Checking Local Ollama daemon...
curl.exe -s http://localhost:11434 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
        echo Starting Ollama background engine...
        start "" /B "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" serve
        timeout /t 3 /nobreak >nul
    ) else (
        echo Note: Ollama not detected in default path. Cloud providers (Groq/Gemini) available.
    )
) else (
    echo Local Ollama engine is active.
)

echo.
echo [2/2] Launching Streamlit Web Application...
echo.
python -m streamlit run app.py
pause
