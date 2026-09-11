@echo off
setlocal
cd /d "%~dp0"

echo ======================================
echo      12D Dil Programi v3.0 Mobile + Desktop Setup
echo ======================================
echo.

set "PY_CMD=py"
where py >nul 2>&1
if errorlevel 1 set "PY_CMD=python"

%PY_CMD% --version >nul 2>&1
if errorlevel 1 goto :python_error

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    %PY_CMD% -m venv ".venv"
    if errorlevel 1 goto :setup_error
) else (
    echo [1/3] Virtual environment already exists.
)

echo [2/3] Updating pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :setup_error

echo [3/3] Installing desktop + mobile requirements...
".venv\Scripts\python.exe" -m pip install -r "requirements.txt"
if errorlevel 1 goto :setup_error

echo.
echo ======================================
echo Setup completed successfully.
echo Microphone no longer requires PyAudio.
echo BASLAT.bat = PC uygulamasi / MOBIL_BASLAT.bat = telefon modu.
echo ======================================
pause
exit /b 0

:python_error
echo.
echo ERROR: Python was not found.
echo Install Python 3.12 or make sure the py/python command works.
pause
exit /b 1

:setup_error
echo.
echo ERROR: Setup failed. Send the error shown above.
pause
exit /b 1
