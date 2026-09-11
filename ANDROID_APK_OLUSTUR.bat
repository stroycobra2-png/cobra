@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0mobile_universal"
call ANDROID_APK_OLUSTUR.bat
exit /b %ERRORLEVEL%
