[app]
# 应用名称（手机上显示的名字）
title = 业闲 - 五子棋

# 包名（需全小写，单词间用下划线或点）
package.name = gomoku
package.domain = org.example

# 版本号（直接写死，避免冲突）
version = 0.1

# 源码目录
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# 依赖（你的项目只用到了 python3 + kivy）
requirements = python3,kivy

# 横屏 + 全屏，五子棋合适
orientation = landscape
fullscreen = true

[buildozer]
# 核心修复：禁止交互式提示（如询问 root 权限），让 CI 自动运行
ignore_existing = True
log_level = 2

[app.android]
# API 级别
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a

# 权限（五子棋不需要特殊权限）
android.permissions = INTERNET

# 引导方式
bootstrap = sdl2
android.entrypoint = org.kivy.android.PythonActivity
