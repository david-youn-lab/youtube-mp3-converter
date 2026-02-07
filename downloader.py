# -*- coding: utf-8 -*-
import yt_dlp
import os
import sys

# 한글 출력 설정
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def download_youtube_as_mp3(url):
    # 저장 경로 설정
    download_path = os.path.join(os.getcwd(), 'downloads')
    os.makedirs(download_path, exist_ok=True)

    # yt-dlp 옵션 설정
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }
        ],
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'noplaylist': True,
    }

    try:
        print(f"다운로드 시작: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("\n✅ 변환 및 저장이 완료되었습니다! (저장 위치: ./downloads)")
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    print("=== 유튜브 MP3 다운로더 ===")
    video_url = input("유튜브 사이트 URL을 입력하세요: ").strip()
    
    if video_url:
        download_youtube_as_mp3(video_url)
    else:
        print("URL이 입력되지 않았습니다.")
