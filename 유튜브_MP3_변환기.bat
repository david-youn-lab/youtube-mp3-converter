@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title 유튜브 MP3 변환기
pushd "%~dp0"
python -X utf8 convert_now.py
pause
