# -*- coding: utf-8 -*-
import yt_dlp
import os
import re
import sys
import subprocess
import shutil

# 한글 출력 설정
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def install_dependencies():
    try:
        import yt_dlp
    except ImportError:
        print(">>> 필수 라이브러리(yt-dlp) 설치 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
        print(">>> 설치 완료! 프로그램을 다시 실행해 주세요.")
        input("엔터를 누르면 종료됩니다.")
        sys.exit()

def clean_filename(filename):
    # 제거할 문구들
    junk_patterns = [
        r'\[.*?\]', r'\(.*?Official.*?\)', r'\(.*?MV.*?\)', r'\(.*?Lyrics.*?\)', 
        r'\(.*?가사.*?\)', r'\(.*?뮤비.*?\)', r'\(.*?뮤직비디오.*?\)',
        r'Official\s*Video', r'Music\s*Video', r'Official\s*Audio', 
        r'M/V', r'MV', r'Music\s*Video', r'Video', r'Audio'
    ]
    
    new_name = filename
    for p in junk_patterns:
        new_name = re.sub(p, '', new_name, flags=re.IGNORECASE)
    
    # 괄호 제거 (속에 남은 내용이 있을 수 있으니 한 번 더 정리)
    new_name = re.sub(r'\(.*?\)', '', new_name)
    new_name = re.sub(r'【.*?】', '', new_name)
    
    # 특수문자 정리 및 공백 정리
    new_name = " ".join(new_name.split()).strip()
    return new_name

def download_music(url):
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
        # 파일명 템플릿: 변환결과 폴더 안에 바로 저장
        'outtmpl': os.path.join(target_dir, '%(title)s.%(ext)s'),
        # 플레이리스트 처리 허용 (여러 곡 주소 대응)
        'noplaylist': False, 
        'ignoreerrors': True,
    }

    try:
        print(f"\n🚀 분석 및 다운로드를 시작합니다 (플레이리스트 포함)...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 주소의 정보를 추출하고 다운로드 진행
            result = ydl.extract_info(url, download=True)
            
            # 다운로드된 곡이 여러 개(플레이리스트)일 경우와 단일 곡일 경우 모두 처리
            if 'entries' in result:
                videos = result['entries']
            else:
                videos = [result]

            print(f"\n--- 정리 작업 시작 ---")
            for video in videos:
                if video is None: continue
                
                # 파일 확장자 고려하여 경로 생성
                original_path = ydl.prepare_filename(video).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                
                if os.path.exists(original_path):
                    dir_name = os.path.dirname(original_path)
                    base_name = os.path.basename(original_path)
                    name_only, ext = os.path.splitext(base_name)
                    
                    # 파일명 세척
                    clean_name = clean_filename(name_only)
                    final_path = os.path.join(dir_name, clean_name + ".mp3")
                    
                    # 이름 변경 및 중복 방지
                    if original_path != final_path:
                        if os.path.exists(final_path):
                            os.remove(final_path)
                        os.rename(original_path, final_path)
                        print(f"✨ 정리됨: {clean_name}.mp3")
                    else:
                        print(f"✅ 완료: {base_name}")

        print(f"\n🎉 모든 작업이 완료되었습니다! '변환결과' 폴더를 확인하세요.")
            
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")

if __name__ == "__main__":
    install_dependencies()
    while True:
        print("\n" + "="*60)
        print("   유튜브 플레이리스트 & 단일 곡 MP3 다운로더")
        print("   (URL을 입력하면 '변환결과' 폴더에 한 곡씩 저장됩니다)")
        print("="*60)
        
        user_url = input("유튜브 URL(믹스/플레이리스트 가능) 입력: ").strip()
        
        if user_url.lower() == 'q':
            break
        if user_url:
            download_music(user_url)
        else:
            print("주소를 입력해 주세요.")