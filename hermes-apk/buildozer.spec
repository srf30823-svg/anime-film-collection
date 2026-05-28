[app]
title = Echo
package.name = echoapp
package.domain = com.echo.anime

# Üst dizinden kaynak al — oneri.py ve data/ dahil edilsin
source.dir = ..
source.include_exts = py,png,jpg,kv,atlas,db,json,txt,ttf
source.include_patterns = oneri.py,data/*,hermes-apk/assets/*,hermes-apk/main.py
source.exclude_dirs = hermes-apk/bin,.buildozer,backups,output,archive,.git,.github,.local
source.main = hermes-apk/main.py

version = 5.3.1

# Bağımlılıklar — pywebview KALDIRILDI (p4a recipe'si yok)
# kivy.uix.webview KALDIRILDI (mevcut değil)
# Native android.webkit.WebView pyjnius ile kullanılıyor
requirements = python3==3.11.0,kivy==2.3.0,android,pyjnius

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE

android.api = 34
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = True

# Karanlık tema uyumu
android.window_softinput_mode = adjustResize
android.add_compile_options = "sourceCompatibility = 1.8", "targetCompatibility = 1.8"

# Grafik
android.wakelock = False

presplash.filename = %(source.dir)s/hermes-apk/assets/presplash.png
icon.filename = %(source.dir)s/hermes-apk/assets/icon.png
presplash.lottie_filename =

# Arka plan rengi (siyah ekranı önler)
android.presplash_color = #0a0a0f

[buildozer]
log_level = 2
warn_on_root = 1
