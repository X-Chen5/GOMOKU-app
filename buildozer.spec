[app]
# 应用名称（手机上显示的名字）
title = 业闲 - 五子棋

# 包名（需全小写，单词间用下划线或点）
package.name = gomoku
package.domain = org.example

# 版本号（这次报错就是缺这个）
version = 0.1
version.regex = __version__ = ['"](.*)['"]
version.filename = %(source.dir)s/main.py

# 源码目录
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# 依赖（你的项目只用到了 python3 + kivy，AI.py/core.py 是纯 py 会自己打进去）
requirements = python3,kivy

# 横屏 + 全屏，五子棋合适
orientation = landscape
fullscreen = true

# 图标（如果有的话放项目根目录，没有就删掉这行）
# icon.filename = %(source.dir)s/icon.png

[buildozer]
log_level = 2

[app.android]
# API 级别
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a

# 权限（五子棋不需要特殊权限，INTERNET 留给 p4a 内部用）
android.permissions = INTERNET

# 引导方式（Kivy 默认 sdl2）
bootstrap = sdl2
android.entrypoint = org.kivy.android.PythonActivity
android.jvm_args = -Djava.library.path=/data/data/%(package.name)s/files/lib
