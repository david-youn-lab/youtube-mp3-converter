# -*- coding: utf-8 -*-
import os
import shutil
import sys

# 한글 출력 설정
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def flatten_music_folder():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(base_dir, "아이폰_전송용_음악")
    
    if not os.path.exists(target_dir):
        print("정리할 폴더가 존재하지 않습니다.")
        return

    print(f"--- 파일 단순화 작업 시작: {target_dir} ---")
    
    # 하위 폴더 탐색
    count = 0
    for root, dirs, files in os.walk(target_dir):
        # 최상위 폴더(target_dir) 자체는 건너뛰고 하위 폴더만 처리
        if root == target_dir:
            continue
            
        for filename in files:
            if filename.endswith(".mp3"):
                src_path = os.path.join(root, filename)
                dst_path = os.path.join(target_dir, filename)
                
                # 파일 이름 중복 방지 (필요 시)
                if os.path.exists(dst_path):
                    name, ext = os.path.splitext(filename)
                    dst_path = os.path.join(target_dir, f"{name}_1{ext}")
                
                try:
                    shutil.move(src_path, dst_path)
                    count += 1
                except Exception as e:
                    print(f"이동 실패 ({filename}): {e}")

    # 비어있는 하위 폴더 삭제
    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)
        if os.path.isdir(item_path):
            try:
                shutil.rmtree(item_path)
            except Exception as e:
                print(f"폴더 삭제 실패 ({item}): {e}")

    print(f"\n✅ 정리 완료! 총 {count}개의 파일이 폴더 구분 없이 모아졌습니다.")

if __name__ == "__main__":
    flatten_music_folder()
