@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title 유튜브 음성 텍스트 변환기 (Whisper + mov_text)
pushd "%~dp0"
python -X utf8 youtube_to_text.py
pause
