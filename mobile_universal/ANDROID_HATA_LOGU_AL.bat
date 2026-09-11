@echo off
chcp 65001 >nul
title 12D Dil Programi - Android Hata Logu
echo.
echo ==============================================
echo   12/D DIL PROGRAMI - TELEFON HATA LOGU
echo ==============================================
echo.
echo Telefonu USB ile bagla ve USB Hata Ayiklama acik olsun.
echo Bu arac WSL Android SDK icindeki adb'yi kullanir.
echo Cikmak icin Ctrl+C.
echo.
wsl.exe -e bash -lc "ADB=\"$HOME/.buildozer/android/platform/android-sdk/platform-tools/adb\"; if [ ! -x \"$ADB\" ]; then ADB=\"$HOME/.12d_mobile_v501_android/.buildozer/android/platform/android-sdk/platform-tools/adb\"; fi; if [ ! -x \"$ADB\" ]; then echo 'adb bulunamadi'; exit 2; fi; \"$ADB\" devices; \"$ADB\" logcat | grep -Ei 'python|kivy|dilprogrami12d|traceback|exception|fatal'"
pause
