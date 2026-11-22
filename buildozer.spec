[app]
title = Net-Lag
package.name = netlag
package.domain = com.tuhin
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# jnius এর কম্প্যাটিবল ভার্সন এবং kivy লক করা হলো
requirements = python3,kivy==2.2.1,cython==0.29.36,jnius>=1.4.0

orientation = portrait
fullscreen = 0

android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, CHANGE_WIFI_STATE, WAKE_LOCK, FOREGROUND_SERVICE

android.api = 33
android.minapi = 21

# NDK 25b এবং ndk_api 24 - এটাই বর্তমানে সবচেয়ে স্ট্যাবল কম্বিনেশন
android.ndk = 25b
android.ndk_api = 24 
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True
