@echo off
setlocal EnableExtensions
chcp 65001 >nul
pushd "%~dp0"
title 12D Dil Programi - iPhone Olustur

:MENU
cls
echo.
echo ==============================================
echo   12/D DIL PROGRAMI - iPHONE OLUSTUR
echo ==============================================
echo.
echo Ekstra Git, GitHub CLI veya Mac kurmana gerek yok.
echo Windows PowerShell + GitHub macOS cloud build kullanilir.
echo.
echo [1] iOS Cloud Build olustur ve indir
echo [2] Gercek imzali iPhone IPA olustur ve indir
echo [3] Apple signing / GitHub bilgisi
echo [4] Cikis
echo.
choice /C 1234 /N /M "Secimin: "

if errorlevel 4 goto END
if errorlevel 3 goto INFO
if errorlevel 2 goto SIGNED
if errorlevel 1 goto CLOUD
goto MENU

:CLOUD
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\iphone_no_install.ps1" -Mode cloud
set "CODE=%ERRORLEVEL%"
echo.
if not "%CODE%"=="0" echo [HATA] iPhone Cloud Build tamamlanamadi. Kod: %CODE%
pause
goto MENU

:SIGNED
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\iphone_no_install.ps1" -Mode signed
set "CODE=%ERRORLEVEL%"
echo.
if not "%CODE%"=="0" echo [HATA] Imzali IPA build tamamlanamadi. Kod: %CODE%
pause
goto MENU

:INFO
cls
echo.
echo ==============================================
echo   ILK KULLANIMDA GEREKENLER
echo ==============================================
echo.
echo Hicbir program indirmen gerekmez.
echo.
echo GitHub senden sadece Personal Access Token ister.
echo Tokeni BAT/PowerShell ekranina yapistirirsin; ekranda gorunmez.
echo.
echo Cloud Build icin token repository/workflow yetkisine sahip olmali.
echo Gercek iPhone IPA icin Apple signing zorunludur.
echo Apple sertifika/sifrelerini bana gonderme.
echo Bunlar GitHub Secrets alaninda tutulur.
echo.
echo Rehber: IPHONE_DIREKT_WINDOWS.md
echo.
if exist "IPHONE_DIREKT_WINDOWS.md" start "" "IPHONE_DIREKT_WINDOWS.md"
pause
goto MENU

:END
popd
endlocal
exit /b 0
