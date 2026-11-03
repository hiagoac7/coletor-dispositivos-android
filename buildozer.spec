[app]
title = Coletor de Dispositivos Android
package.name = coletordispositivos
package.domain = io.github.hiagoac7
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 0.2
requirements = python3,kivy,pyjnius
orientation = portrait
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 0
