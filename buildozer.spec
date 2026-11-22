[app]
# (str) Title of your application
title = Net-Lag

# (str) Package name
package.name = netlag

# (str) Package domain (needed for android/ios packaging)
package.domain = com.tuhin

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 1.0

# (list) Application requirements
requirements = python3,kivy

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, CHANGE_WIFI_STATE, WAKE_LOCK, FOREGROUND_SERVICE, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True
