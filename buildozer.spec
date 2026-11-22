[app]
title = Net-Lag
package.name = netlag
package.domain = com.tuhin
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
# কিবি এবং জিনিয়াসের সুনির্দিষ্ট ভার্সন লক করা হলো যাতে বিল্ড ফেইল না করে
requirements = python3,kivy==2.2.1,cython==0.29.36,jnius,android,pillow
orientation = portrait
fullscreen = 0

# পারমিশনসমূহ
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, CHANGE_WIFI_STATE, WAKE_LOCK, FOREGROUND_SERVICE

android.api = 33
android.minapi = 21
android.ndk = 25b
# ndk_api 21 থেকে 24 করা হলো কারণ এটি NDK 25b এর সাথে ভালো কাজ করে
android.ndk_api = 24 
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True
