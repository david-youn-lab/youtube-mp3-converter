# -*- coding: utf-8 -*-
import yt_dlp
import os
import sys
from datetime import datetime, timedelta

# 한글 출력 설정
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def download_latest_kpop_100():
    # 현재 날짜로부터 3개월 전 날짜 계산 (YYYYMMDD 형식)
    three_months_ago = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')

    # 스크립트 위치 기준 변환결과 폴더에 저장
    base_dir = os.path.dirname(os.path.abspath(__file__))
    current_path = os.path.join(base_dir, '변환결과')
    os.makedirs(current_path, exist_ok=True)
    
    print(f"--- 최신 가요 100곡 다운로드 시작 (기준일: {three_months_ago} 이후) ---")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        # 현재 폴더에 파일명 그대로 저장
        'outtmpl': os.path.join(current_path, '%(title)s.%(ext)s'),
        # 검색어 기반 100개 추출
        'default_search': 'ytsearch100',
        'max_downloads': 100,
        # 최근 3개월 이내 영상만 필터링
        'dateafter': three_months_ago,
        'noplaylist': True,
        'quiet': False,
    }

    try:
        # '최신 한국 가요' 검색어로 100곡 다운로드 시도
        search_query = "2026 최신 가요 멜론차트 Top 100"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([search_query])
        print("\n✅ 모든 다운로드가 완료되었습니다!")
    except Exception as e:
        print(f"\n❌ 작업 중 오류 발생: {e}")

if __name__ == "__main__":
    download_latest_kpop_100()
