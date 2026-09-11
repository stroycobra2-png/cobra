@echo off
setlocal EnableExtensions
chcp 65001 >nul
pushd "%~dp0"
title 12D Android P4A Repair

echo.
echo ==============================================
echo   12/D ANDROID - P4A PYTHON 3.14 REPAIR
echo ==============================================
echo.
echo Bu arac eski p4a master/build cache'ini temizler.
echo Uygulama kaynak kodlarini ve profil verilerini silmez.
echo.

where wsl.exe >nul 2>nul
if errorlevel 1 (
    echo [HATA] WSL bulunamadi.
    pause
    exit /b 1
)

set "LINUX_DIR_FILE=%TEMP%\12d_p4a_path_%RANDOM%.txt"
wsl.exe -e wslpath -a "%CD%" > "%LINUX_DIR_FILE%" 2>nul
set "LINUX_DIR="
set /p LINUX_DIR=<"%LINUX_DIR_FILE%"
del "%LINUX_DIR_FILE%" >nul 2>nul

if not defined LINUX_DIR (
    echo [HATA] WSL yolu hesaplanamadi.
    pause
    exit /b 2
)

wsl.exe -e bash -lc "rm -rf \"$HOME/.12d_android_builder/project/.buildozer/android/platform/python-for-android\" \"$HOME/.12d_android_builder/project/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a\" \"$HOME/.12d_android_builder/venv\" \"$HOME/.12d_android_builder/.py314_p4a_develop_v403\""

if errorlevel 1 (
    echo [HATA] Cache temizlenemedi.
    pause
    exit /b 3
)

echo.
echo [OK] Eski p4a/build venv cache temizlendi.
echo Simdi ANDROID_APK_OLUSTUR.bat dosyasini calistir.
echo.
pause
popd
endlocal
