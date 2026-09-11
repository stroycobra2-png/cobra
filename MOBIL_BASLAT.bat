@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo 12D Dil Programi henuz kurulmamis.
    call "KURULUM.bat"
    if errorlevel 1 exit /b 1
)

".venv\Scripts\python.exe" -c "import flask, waitress" >nul 2>&1
if errorlevel 1 (
    echo Mobil paketler eksik. Kuruluyor...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto :error
)

echo.
echo Telefon ve bilgisayar ayni Wi-Fi aginda olmali.
echo Asagida yazacak adresi telefondan ac.
echo.
".venv\Scripts\python.exe" "mobile_server.py"
exit /b 0

:error
echo Mobil kurulum basarisiz.
pause
exit /b 1
