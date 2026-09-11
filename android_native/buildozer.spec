[app]
title = 12D Dil Programi
package.name = dilprogrami12d
package.domain = tr.okul
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,kv,ttf
version = 4.0.3
requirements = python3,kivy,plyer
orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png

android.permissions = INTERNET,RECORD_AUDIO
android.api = 36
android.ndk = 28c
android.minapi = 23
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 1
