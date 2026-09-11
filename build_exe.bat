@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Run KURULUM.bat first.
    pause
    exit /b 1
)

echo Installing PyInstaller...
".venv\Scripts\python.exe" -m pip install pyinstaller
if errorlevel 1 goto :build_error

echo Building 12D_Dil_Programi.exe...
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --windowed --name 12D_Dil_Programi "main.py"
if errorlevel 1 goto :build_error

echo.
echo Build completed. Check the dist\12D_Dil_Programi folder.
pause
exit /b 0

:build_error
echo.
echo ERROR: Build failed. Send the error shown above.
pause
exit /b 1
