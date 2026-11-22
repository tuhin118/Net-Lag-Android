[app]
title = Net-Lag
package.name = netlag
package.domain = com.tuhin
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
# jnius এবং kivy-এর সুনির্দিষ্ট ভার্সন লক করা হলো
requirements = python3,kivy==2.2.1,cython==0.29.36,jnius

# অপ্রয়োজনীয় 'android' এবং 'pillow' বাদ দেওয়া হলো
orientation = portrait
fullscreen = 0

android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, CHANGE_WIFI_STATE, WAKE_LOCK, FOREGROUND_SERVICE

android.api = 33
android.minapi = 21

# NDK 25b এর বদলে 23b ব্যবহার করা হলো (অনেক বেশি স্ট্যাবল)
android.ndk = 23b 
android.ndk_api = 24 
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True
