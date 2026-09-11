@echo off
setlocal EnableExtensions
chcp 65001 >nul
pushd "%~dp0"
title 12D Universal Mobile - Android APK v5.0.1

echo.
echo ==============================================
echo   12/D UNIVERSAL MOBILE - ANDROID APK
echo   v5.0.1 CLEAN BUILDER
echo ==============================================
echo.

where wsl.exe >nul 2>nul
if errorlevel 1 (
    echo [HATA] WSL bulunamadi.
    pause
    popd
    exit /b 1
)

set "PROBE=%TEMP%\12d_wsl_%RANDOM%.txt"
wsl.exe -e sh -lc "printf 12D_OK" > "%PROBE%" 2>&1
findstr /c:"12D_OK" "%PROBE%" >nul 2>nul
if errorlevel 1 (
    echo [HATA] Calisan Ubuntu/Linux dagitimi bulunamadi.
    type "%PROBE%"
    del "%PROBE%" >nul 2>nul
    pause
    popd
    exit /b 2
)
del "%PROBE%" >nul 2>nul

set "PATHFILE=%TEMP%\12d_path_%RANDOM%.txt"
wsl.exe -e wslpath -a "%CD%" > "%PATHFILE%" 2>nul
set "LINUX_DIR="
set /p LINUX_DIR=<"%PATHFILE%"
del "%PATHFILE%" >nul 2>nul

if not defined LINUX_DIR (
    echo [HATA] Windows yolu WSL yoluna cevrilemedi.
    pause
    popd
    exit /b 3
)

echo Proje : %CD%
echo WSL   : %LINUX_DIR%
echo.
echo NOT: Bu paket eski android_native builder'ini kullanmaz.
echo Sadece mobile_universal icindeki temiz ARM64 builder calisir.
echo.

wsl.exe -e bash "%LINUX_DIR%/BUILD_ANDROID.sh"
set "RESULT=%ERRORLEVEL%"

if not "%RESULT%"=="0" (
    echo.
    echo ==============================================
    echo [HATA] Android build basarisiz. Kod: %RESULT%
    echo Tam log: %CD%\android_build.log
    echo ==============================================
    echo.
    pause
    popd
    exit /b %RESULT%
)

echo.
echo ==============================================
echo APK HAZIR
echo ==============================================
echo %CD%\bin
if exist "bin\*.apk" dir /b "bin\*.apk"
echo.
pause
popd
endlocal
