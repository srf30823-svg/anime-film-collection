[app]
title = OWL Anime & Film
package.name = owl_anime_film
package.domain = com.owl.anime
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,json,txt
version = 5.1.0
requirements = python3,kivy==2.3.0,pillow,android,pyjnius
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.archs = arm64-v8a
android.accept_sdk_license = True
presplash.filename = assets/presplash.png
icon.filename = assets/logo.png
log_level = 2
warn_on_root = 1
[buildozer]
log_level = 2
warn_on_root = 1
