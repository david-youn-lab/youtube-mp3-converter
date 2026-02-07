@echo off
chcp 65001 > nul
title 유튜브 음성 텍스트 변환기 (Whisper + mov_text)
pushd "%~dp0"
python youtube_to_text.py
pause
