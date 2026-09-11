[app]
title = 12D Dil Programi
package.name = dilprogrami12d
package.domain = tr.okul
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,kv,ttf
version = 5.3.9

# Python 3.14 is pinned on both target + host to avoid recipe mismatch.
requirements = python3==3.14.2,hostpython3==3.14.2,kivy

orientation = portrait
# In-app Turkish Q keyboard is used on Android/iOS text fields.
fullscreen = 0
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png

android.permissions = INTERNET,RECORD_AUDIO
android.api = 36
android.minapi = 24
android.ndk = 29

# IMPORTANT: arm64 only.
# The old package accidentally exposed an obsolete dual-ABI builder
# (arm64-v8a + armeabi-v7a) which is where the user's failing command came from.
android.archs = arm64-v8a
android.accept_sdk_license = True
p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 1
