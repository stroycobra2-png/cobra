@echo off
setlocal
chcp 65001 >nul
title 12D Dil Programi - WSL Ubuntu Kurulumu

echo.
echo ==============================================
echo   WSL + UBUNTU KURULUMU
echo ==============================================
echo.
echo Bu islem Windows yonetici izni isteyecektir.
echo Kurulumdan sonra bilgisayari yeniden baslatman gerekebilir.
echo.
pause

powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath 'wsl.exe' -ArgumentList '--install','-d','Ubuntu' -Verb RunAs -Wait"

if errorlevel 1 (
    echo.
    echo [HATA] WSL/Ubuntu kurulum komutu tamamlanamadi.
    echo Yonetici olarak PowerShell acip su komutu calistir:
    echo     wsl --install -d Ubuntu
    echo.
    pause
    exit /b 1
)

echo.
echo ==============================================
echo Komut tamamlandi.
echo ==============================================
echo.
echo 1. Windows yeniden baslatma isterse bilgisayari yeniden baslat.
echo 2. Baslat menusunden Ubuntu'yu ac.
echo 3. Linux kullanici adi ve sifreni olustur.
echo 4. Ubuntu terminalinde su komutu test et:
echo       python3 --version
echo 5. Sonra ANDROID_APK_OLUSTUR.bat dosyasini tekrar calistir.
echo.
pause
endlocal
