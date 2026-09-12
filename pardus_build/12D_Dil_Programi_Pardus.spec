# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas=[]
binaries=[]
hiddenimports=['difflib','numpy','sounddevice','speech_recognition','pyttsx3','pyttsx3.drivers','pyttsx3.drivers.espeak']
for package in ('sounddevice','speech_recognition','pyttsx3'):
    try:
        d,b,h=collect_all(package); datas += d; binaries += b; hiddenimports += h
    except Exception:
        pass

a = Analysis(
    ['main.py'], pathex=['.'], binaries=binaries, datas=datas,
    hiddenimports=hiddenimports, hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=['app.ui','win32com','pythoncom','pywintypes'], noarchive=False, optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True,
    name='12D_Dil_Programi', debug=False, bootloader_ignore_signals=False,
    strip=False, upx=False, console=False,
)
coll = COLLECT(
    exe, a.binaries, a.datas, strip=False, upx=False,
    name='12D_Dil_Programi'
)
