[app]
title = 业闲 - 五子棋
package.name = gomoku
package.domain = org.example
version = 0.1

source.dir = .
source.include_exts = py,png,jpg,kv,ttf,otf
source.exclude_exts = git,pyc,pyo
source.exclude_dirs = tests,__pycache__,docs

requirements = python3,kivy

orientation = landscape
fullscreen = true

bootstrap = sdl2
android.entrypoint = org.kivy.android.PythonActivity

[buildozer]
ignore_existing = True

[app.android]
android.api = 33
android.minapi = 21
android.targetapi = 33
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.permissions = INTERNET

environment = BUILDZER_NO_INTERACTION=1, PYTHONUNBUFFERED=1
