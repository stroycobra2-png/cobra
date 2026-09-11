@echo off
setlocal
chcp 65001 >nul
title 12D Android v5.0.1 Build Sifirla
echo.
echo Bu islem sadece v5.0.1 Android build cache'ini siler.
echo Uygulama kaynak koduna veya profil verilerine dokunmaz.
echo.
choice /C EH /N /M "E=Temizle, H=Hayir: "
if errorlevel 2 exit /b 0
wsl.exe -e bash -lc "rm -rf \"$HOME/.12d_mobile_v501_android\" && echo [OK] v5.0.1 build cache temizlendi."
echo.
pause
