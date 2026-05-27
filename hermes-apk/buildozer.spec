[app]
title = Echo
package.name = echo.anime
package.domain = com.echo.anime
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,json,txt
version = 5.2.0
requirements = python3,kivy==2.3.0,android,pyjnius
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 21
android.archs = arm64-v8a
android.accept_sdk_license = True
presplash.filename = assets/presplash.png
icon.filename = assets/icon.png
log_level = 2
warn_on_root = 1
[buildozer]
log_level = 2
warn_on_root = 1
