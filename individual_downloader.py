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

def download_100_individual_songs():
    # 3개월 전 날짜 계산
    three_months_ago = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')
    current_path = os.path.join(os.getcwd(), '변환결과')
    os.makedirs(current_path, exist_ok=True)
    
    print(f"--- 개별 곡 100개 다운로드 시작 (기준: {three_months_ago} 이후 신곡) ---")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(current_path, '%(title)s.%(ext)s'),
        'default_search': 'ytsearch100',
        'max_downloads': 100,
        'dateafter': three_months_ago,
        # 10분(600초) 이상의 영상은 모음집으로 간주하여 제외
        'match_filter': yt_dlp.utils.match_filter_func('duration < 600 & !is_live'),
        'noplaylist': True,
        'ignoreerrors': True, # 오류 나면 다음 곡으로 진행
    }

    # 다양한 검색어 조합으로 최대한 개별 곡 확보
    search_queries = [
        "2026 최신 가요 신곡",
        "K-POP 2026 New Songs Official Audio",
        "2025 12월 가요 신곡",
        "2026 1월 가요 신곡"
    ]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for query in search_queries:
                print(f"\n🔍 검색어 실행 중: {query}")
                ydl.download([query])
        print("\n✅ 개별 곡 다운로드 시도가 완료되었습니다!")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")

if __name__ == "__main__":
    download_100_individual_songs()
