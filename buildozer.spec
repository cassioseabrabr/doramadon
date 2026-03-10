[app]
title = DoramaDown
package.name = doramadown
package.domain = org.kwaiboost
source.dir = .
source.include_exts = py
version = 1.0
requirements = python3,kivy==2.3.0,telethon,cryptg,pillow,certifi
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
[buildozer]
log_level = 2
warn_on_root = 1
