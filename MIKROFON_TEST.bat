@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo 12D Dil Programi is not installed yet. Run KURULUM.bat first.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" "mic_test.py"
echo.
pause
