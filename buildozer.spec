[app]
# 应用名称（手机上显示的名字）
title = 业闲 - 五子棋

# 包名（需全小写，单词间用下划线或点）
package.name = gomoku
package.domain = org.example

# 版本号
version = 0.1

# 源码目录
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# 依赖
requirements = python3,kivy

# 屏幕方向
orientation = landscape
fullscreen = true

[buildozer]
# 核心修正：这里设置为 true，告诉 buildozer 不要问任何问题，直接强制执行
ignore_existing = True
log_level = 2

[app.android]
# API 级别
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a

# 权限
android.permissions = INTERNET

# 引导方式
bootstrap = sdl2
android.entrypoint = org.kivy.android.PythonActivity
