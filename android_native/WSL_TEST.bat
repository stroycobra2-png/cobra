@echo off
setlocal
chcp 65001 >nul
title 12D - WSL Test

echo === WSL DOSYA KONTROLU ===
where wsl.exe

echo.
echo === WSL STATUS ===
wsl.exe --status

echo.
echo === KURULU DAGITIMLAR ===
wsl.exe -l -v

echo.
echo === LINUX KOMUT TESTI ===
wsl.exe -e sh -lc "echo 12D_WSL_OK && uname -a && python3 --version"

echo.
pause
endlocal
