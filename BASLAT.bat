@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo 12D Dil Programi is not installed yet.
    echo Running setup first...
    call "KURULUM.bat"
    if errorlevel 1 exit /b 1
)

echo Checking required packages...
".venv\Scripts\python.exe" -c "import PySide6, pyttsx3, speech_recognition, sounddevice, numpy" >nul 2>&1
if errorlevel 1 (
    echo Missing package detected. Updating dependencies...
    ".venv\Scripts\python.exe" -m pip install -r "requirements.txt"
    if errorlevel 1 (
        echo.
        echo ERROR: Dependency installation failed.
        pause
        exit /b 1
    )
)

".venv\Scripts\python.exe" "main.py"
if errorlevel 1 (
    echo.
    echo 12D Dil Programi closed with an error.
    echo Send the error message shown above.
    pause
    exit /b 1
)
exit /b 0
