[app]
title = 业闲 - 五子棋
package.name = gomoku
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv

requirements = python3,kivy

# 国内镜像，加速 pip 下载
pypi_mirror = https://pypi.tuna.tsinghua.edu.cn/simple

orientation = landscape
fullscreen = true

[buildozer]
log_level = 2

[app.android]
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True