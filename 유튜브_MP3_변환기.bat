@echo off
chcp 65001 > nul
title 유튜브 MP3 변환기
pushd "%~dp0"
python convert_now.py
pause