@echo off
setlocal EnableExtensions
chcp 65001 >nul
pushd "%~dp0"
title 12D Dil Programi - Android APK Olustur

echo.
echo ==============================================
echo   12/D DIL PROGRAMI - ANDROID APK BUILDER
echo ==============================================
echo.

echo [1/4] WSL kontrol ediliyor...
where wsl.exe >nul 2>nul
if errorlevel 1 (
    echo.
    echo [HATA] WSL Windows'ta bulunamadi.
    echo WSL_UBUNTU_KUR.bat dosyasini Yonetici olarak calistir.
    echo.
    pause
    popd
    exit /b 1
)

echo [2/4] Linux/Ubuntu dagitimi test ediliyor...
set "PROBE_FILE=%TEMP%\12d_wsl_probe_%RANDOM%.txt"
wsl.exe -e sh -lc "printf 12D_WSL_OK" > "%PROBE_FILE%" 2>&1
findstr /c:"12D_WSL_OK" "%PROBE_FILE%" >nul 2>nul
if errorlevel 1 (
    echo.
    echo [HATA] WSL var ancak calisan Ubuntu/Linux dagitimi yok.
    echo WSL_UBUNTU_KUR.bat dosyasini calistir.
    echo Kurulumdan sonra Ubuntu'yu en az bir kez ac.
    echo.
    type "%PROBE_FILE%"
    del "%PROBE_FILE%" >nul 2>nul
    pause
    popd
    exit /b 2
)
del "%PROBE_FILE%" >nul 2>nul

echo [3/4] Proje yolu Linux formatina cevriliyor...
set "LINUX_DIR_FILE=%TEMP%\12d_wsl_path_%RANDOM%.txt"
wsl.exe -e wslpath -a "%CD%" > "%LINUX_DIR_FILE%" 2>nul
set "LINUX_DIR="
set /p LINUX_DIR=<"%LINUX_DIR_FILE%"
del "%LINUX_DIR_FILE%" >nul 2>nul

if not defined LINUX_DIR (
    echo.
    echo [HATA] Proje yolu WSL formatina cevrilemedi.
    echo.
    pause
    popd
    exit /b 3
)

echo     Windows: %CD%
echo     Linux  : %LINUX_DIR%
echo.
echo [4/4] Android APK derlemesi baslatiliyor...
echo.
echo NOT:
echo - Kaynak proje Windows klasorunde kalacak.
echo - Gercek derleme Linux home klasorunde yapilacak.
echo - APK tamamlaninca bu klasordeki bin\ dizinine kopyalanacak.
echo.

wsl.exe -e bash "%LINUX_DIR%/BUILD_APK.sh"
set "BUILD_RESULT=%ERRORLEVEL%"

if not "%BUILD_RESULT%"=="0" (
    echo.
    echo ==============================================
    echo [HATA] APK derlemesi tamamlanamadi. Kod: %BUILD_RESULT%
    echo Yukaridaki EN SON hata satirlarini ChatGPT'ye gonderebilirsin.
    echo ==============================================
    echo.
    pause
    popd
    exit /b %BUILD_RESULT%
)

echo.
echo ==============================================
echo   APK DERLEMESI TAMAMLANDI
echo ==============================================
echo APK:
echo %CD%\bin
echo.

if exist "bin\*.apk" (
    dir /b "bin\*.apk"
) else (
    echo [UYARI] Derleme tamamlandi ancak Windows bin klasorunde APK bulunamadi.
)

echo.
pause
popd
endlocal
