# -*- coding: utf-8 -*-
import os
import re
import shutil
import sys

# 한글 출력 설정
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def organize_for_iphone():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(current_dir, "아이폰_전송용_음악")
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    # MP3 파일 목록 가져오기
    files = [f for f in os.listdir(current_dir) if f.endswith(".mp3")]
    
    # 제거할 불필요한 문구들 (정규식)
    clean_patterns = [
        r'\[.*?\]', r'\(.*?\)', r'（.*?）',
        r'Official', r'MV', r'Music Video', r'Lyrics', r'가사', r'뮤직비디오'
    ]
    
    print(f"--- 파일 정리 시작 ({len(files)}곡) ---")
    
    for filename in files:
        new_name = filename
        # 문구 제거
        for pattern in clean_patterns:
            new_name = re.sub(pattern, '', new_name, flags=re.IGNORECASE)
        
        # 공백 정리
        new_name = " ".join(new_name.split()).strip()
        if not new_name.endswith(".mp3"):
            new_name += ".mp3"
            
        # 가수명 추출 시도 (보통 '가수 - 제목' 또는 '가수 _ 제목' 형식)
        artist = "기타"
        for separator in ['-', '_', '–']:
            if separator in new_name:
                artist = new_name.split(separator)[0].strip()
                break
        
        # 아티스트 폴더 생성
        artist_folder = os.path.join(target_dir, artist)
        if not os.path.exists(artist_folder):
            os.makedirs(artist_folder)
            
        # 파일 이동 및 이름 변경
        src = os.path.join(current_dir, filename)
        dst = os.path.join(artist_folder, new_name)
        
        try:
            shutil.move(src, dst)
            print(f"정리 완료: {new_name} -> {artist}/")
        except Exception as e:
            print(f"이동 실패 ({filename}): {e}")

    print(f"\n✅ 모든 파일이 '{target_dir}' 폴더로 깔끔하게 정리되었습니다!")

if __name__ == "__main__":
    organize_for_iphone()
