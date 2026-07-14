# ========================================================
# 业闲 - 五子棋 (Gomoku) - 终极修复版 buildozer.spec
# ========================================================

[app]
# 1. 基本信息
title = 业闲 - 五子棋
package.name = gomoku
package.domain = org.example

# 2. 版本控制 (解决 version 冲突)
version = 0.1

# 3. 源码与资源
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
source.exclude_exts = git,pyc,pyo
source.exclude_dirs = tests,__pycache__,docs

# 4. 依赖项
requirements = python3,kivy

# 5. 应用行为
orientation = landscape
fullscreen = true
bootstrap = sdl2
android.entrypoint = org.kivy.android.PythonActivity

# ========================================================
# 核心修复区：解决 "running as root" 和交互问题
# ========================================================
[buildozer]
ignore_existing = True

# ========================================================
# Android 专项配置
# ========================================================
[app.android]
# 1. API 级别
android.api = 33
android.minapi = 21
android.targetapi = 33

# 2. NDK 版本
android.ndk = 25b

# 3. CPU 架构
android.archs = arm64-v8a,armeabi-v7a

# 4. 权限
android.permissions = INTERNET

# ========================================================
# 全局环境变量 (Buildozer 会读取这些)
# ========================================================
environment = BUILDZER_NO_INTERACTION=1, PYTHONUNBUFFERED=1
