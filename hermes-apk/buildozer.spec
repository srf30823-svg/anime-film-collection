[app]
title = Echo
package.name = echo.anime
package.domain = com.echo.anime
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,json,txt,ttf
version = 5.3.0
requirements = python3,kivy==2.3.0,android,pyjnius,pywebview
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE
android.api = 34
android.minapi = 21
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True
presplash.filename = %(source.dir)s/assets/presplash.png
icon.filename = %(source.dir)s/assets/icon.png
log_level = 2
warn_on_root = 1
# WebView desteği
android.add_aars =
p4a.local_recipes =
# Multi-window sorunu çözümü
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
