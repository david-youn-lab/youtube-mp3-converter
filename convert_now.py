# -*- coding: utf-8 -*-
import yt_dlp
import os
import re
import shutil
import sys

# 한글 출력을 위한 설정
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def clean_filename(filename):
    # 불필요한 문구 제거 (정규식 사용)
    patterns = [
        r'\[.*?\]', r'\(.*?\)', r'【.*?】',
        r'Official', r'MV', r'Music Video', r'Lyrics',
        '가사', '뮤직비디오', '오피셜'
    ]
    new_name = filename
    for p in patterns:
        new_name = re.sub(p, '', new_name, flags=re.IGNORECASE)
    return " ".join(new_name.split()).strip()

def process_url(url):
    # 저장 폴더: 스크립트 위치 기준 변환결과
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(base_dir, "변환결과")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(target_dir, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': False,
    }

    try:
        print("\n>>> 다운로드 및 변환 작업을 시작합니다...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # 파일 확장자 처리 (webm/m4a -> mp3)
            orig_file = ydl.prepare_filename(info)
            base, _ = os.path.splitext(orig_file)
            original_mp3 = base + ".mp3"
            
            # 파일명 정리
            pure_name = clean_filename(os.path.basename(base))
            final_mp3 = os.path.join(target_dir, pure_name + ".mp3")
            
            # 이름 변경 (중복 시 번호 추가)
            if os.path.exists(original_mp3):
                if original_mp3 != final_mp3:
                    if os.path.exists(final_mp3):
                        os.remove(final_mp3)
                    os.rename(original_mp3, final_path := final_mp3)
                else:
                    final_path = original_mp3
                
                print(f"\n[완료] {os.path.basename(final_path)}")
                print(f"[저장] {target_dir}")
            
    except Exception as e:
        print(f"\n[오류] 발생: {str(e)}")

if __name__ == "__main__":
    while True:
        print("\n" + "="*50)
        print("   Youtube to MP3 Downloader (변환결과 폴더 자동 저장)")
        print("   (종료하시려면 'q'를 입력하세요)")
        print("="*50)
        url_input = input("유튜브 URL 입력: ").strip()
        
        if url_input.lower() == 'q':
            break
        if url_input:
            process_url(url_input)
        else:
            print("주소를 정확히 입력해 주세요.")