@echo off
setlocal
chcp 65001 >nul
title 12D Android Build Cache Temizle
echo.
echo Bu islem Linux tarafindaki 12/D Android build cache'ini temizler.
echo Uygulama kaynak kodlarina dokunmaz.
echo.
choice /C EH /N /M "E=Temizle, H=Hayir: "
if errorlevel 2 exit /b 0
wsl.exe -e bash -lc "rm -rf \"$HOME/.12d_android_builder\" && echo Build cache temizlendi."
echo.
pause
