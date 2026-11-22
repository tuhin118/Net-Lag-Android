
[app]

title = Net-Lag
package.name = netlag
package.domain = com.tuhin

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.1

requirements = python3,kivy==2.2.1

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,WAKE_LOCK

android.api = 33
android.minapi = 21

android.ndk = 25b
android.ndk_api = 24

android.archs = arm64-v8a

android.accept_sdk_license = True
android.allow_backup = True

[buildozer]

log_level = 2
warn_on_root = 1
