# -*- coding: utf-8 -*-
import yt_dlp
import whisper
import os
import sys
import re
import subprocess
import time

# 한글 출력 설정
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass


def check_dependencies():
    """필수 라이브러리 확인 및 설치"""
    missing = []
    try:
        import yt_dlp
    except ImportError:
        missing.append("yt-dlp")
    try:
        import whisper
    except ImportError:
        missing.append("openai-whisper")

    if missing:
        print(f">>> 필수 라이브러리 설치 중: {', '.join(missing)}")
        for pkg in missing:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        print(">>> 설치 완료! 프로그램을 다시 실행해 주세요.")
        input("엔터를 누르면 종료됩니다.")
        sys.exit()


def clean_filename(name):
    """파일명에서 특수문자 제거"""
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    name = " ".join(name.split()).strip()
    return name


def download_audio(url, output_dir):
    """유튜브에서 오디오 다운로드 (WAV 형식)"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': False,
    }

    print("\n[1/3] 유튜브에서 오디오 다운로드 중...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get('title', 'output')
        clean_title = clean_filename(title)

        # 다운로드된 WAV 파일 경로 찾기
        orig_file = ydl.prepare_filename(info)
        base, _ = os.path.splitext(orig_file)
        wav_path = base + ".wav"

        # 파일명 정리
        if os.path.exists(wav_path):
            new_wav = os.path.join(output_dir, clean_title + ".wav")
            if wav_path != new_wav:
                if os.path.exists(new_wav):
                    os.remove(new_wav)
                os.rename(wav_path, new_wav)
                wav_path = new_wav

        print(f"    다운로드 완료: {os.path.basename(wav_path)}")
        return wav_path, clean_title


def transcribe_audio(wav_path, model_name="turbo", language="ko"):
    """Whisper를 사용하여 음성을 텍스트로 변환"""
    print(f"\n[2/3] 음성 인식 중 (모델: {model_name}, 언어: {language})...")
    print("    (첫 실행 시 모델 다운로드에 시간이 걸릴 수 있습니다)")

    model = whisper.load_model(model_name)
    result = model.transcribe(wav_path, language=language, verbose=False)

    print("    음성 인식 완료!")
    return result


def format_timestamp(seconds):
    """초를 SRT 타임스탬프 형식으로 변환"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def save_results(result, output_dir, title):
    """변환 결과를 다양한 형식으로 저장"""
    print(f"\n[3/3] 결과 저장 중...")

    # 1) 전체 텍스트 (.txt)
    txt_path = os.path.join(output_dir, title + ".txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"제목: {title}\n")
        f.write(f"{'=' * 60}\n\n")
        f.write(result['text'].strip())
        f.write(f"\n\n{'=' * 60}\n")
        f.write(f"변환 언어: {result.get('language', 'unknown')}\n")
    print(f"    텍스트 파일: {os.path.basename(txt_path)}")

    # 2) SRT 자막 파일 (.srt)
    srt_path = os.path.join(output_dir, title + ".srt")
    with open(srt_path, 'w', encoding='utf-8') as f:
        for i, seg in enumerate(result['segments'], 1):
            start = format_timestamp(seg['start'])
            end = format_timestamp(seg['end'])
            text = seg['text'].strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
    print(f"    자막 파일:   {os.path.basename(srt_path)}")

    # 3) 타임라인 포함 텍스트 (.timeline.txt)
    timeline_path = os.path.join(output_dir, title + ".timeline.txt")
    with open(timeline_path, 'w', encoding='utf-8') as f:
        f.write(f"제목: {title}\n")
        f.write(f"{'=' * 60}\n\n")
        for seg in result['segments']:
            start_min = int(seg['start'] // 60)
            start_sec = int(seg['start'] % 60)
            text = seg['text'].strip()
            f.write(f"[{start_min:02d}:{start_sec:02d}] {text}\n")
    print(f"    타임라인:    {os.path.basename(timeline_path)}")

    return txt_path, srt_path, timeline_path


def embed_subtitles_mov_text(wav_path, srt_path, output_dir, title):
    """FFmpeg mov_text 코덱으로 자막이 포함된 MP4 생성"""
    mp4_path = os.path.join(output_dir, title + "_자막포함.mp4")

    cmd = [
        'ffmpeg', '-y',
        '-i', wav_path,
        '-i', srt_path,
        '-c:a', 'aac',
        '-c:s', 'mov_text',
        '-metadata:s:s:0', 'language=kor',
        mp4_path
    ]

    try:
        print(f"\n    mov_text 자막 포함 MP4 생성 중...")
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"    자막 MP4:    {os.path.basename(mp4_path)}")
        return mp4_path
    except subprocess.CalledProcessError as e:
        print(f"    (mov_text MP4 생성 실패: {e.stderr[:200] if e.stderr else 'unknown error'})")
        return None
    except FileNotFoundError:
        print("    (FFmpeg를 찾을 수 없습니다)")
        return None


def select_model():
    """사용할 Whisper 모델 선택"""
    models = {
        '1': ('turbo', '빠름, 정확도 높음 (권장)'),
        '2': ('base', '매우 빠름, 정확도 보통'),
        '3': ('small', '보통 속도, 정확도 좋음'),
        '4': ('medium', '느림, 정확도 매우 좋음'),
        '5': ('large-v3', '매우 느림, 최고 정확도'),
    }

    print("\n--- Whisper 모델 선택 ---")
    for key, (name, desc) in models.items():
        print(f"  {key}. {name:15s} - {desc}")

    choice = input("\n모델 번호 선택 (기본: 1): ").strip()
    if choice in models:
        return models[choice][0]
    return 'turbo'


def select_language():
    """변환 언어 선택"""
    langs = {
        '1': ('ko', '한국어'),
        '2': ('en', '영어'),
        '3': ('ja', '일본어'),
        '4': ('zh', '중국어'),
        '5': (None, '자동 감지'),
    }

    print("\n--- 언어 선택 ---")
    for key, (code, name) in langs.items():
        print(f"  {key}. {name}")

    choice = input("\n언어 번호 선택 (기본: 1 한국어): ").strip()
    if choice in langs:
        return langs[choice][0]
    return 'ko'


def process_url(url, model_name, language):
    """전체 처리 파이프라인"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "변환결과")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    start_time = time.time()

    try:
        # 1단계: 오디오 다운로드
        wav_path, title = download_audio(url, output_dir)

        # 2단계: 음성 인식
        result = transcribe_audio(wav_path, model_name, language)

        # 3단계: 결과 저장
        txt_path, srt_path, timeline_path = save_results(result, output_dir, title)

        # 4단계: mov_text 자막 포함 MP4 생성
        embed_subtitles_mov_text(wav_path, srt_path, output_dir, title)

        # WAV 파일 삭제 (용량이 크므로)
        try:
            os.remove(wav_path)
        except:
            pass

        elapsed = time.time() - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        print(f"\n{'=' * 60}")
        print(f"  모든 작업 완료! (소요 시간: {minutes}분 {seconds}초)")
        print(f"  저장 위치: {output_dir}")
        print(f"{'=' * 60}")

        # 변환된 텍스트 미리보기
        print(f"\n--- 텍스트 미리보기 (처음 500자) ---")
        preview = result['text'].strip()[:500]
        print(preview)
        if len(result['text'].strip()) > 500:
            print("... (전체 내용은 txt 파일을 확인하세요)")
        print()

    except Exception as e:
        print(f"\n[오류] {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_dependencies()

    print()
    print("=" * 60)
    print("   유튜브 음성 -> 텍스트 변환기 (Whisper + mov_text)")
    print("   YouTube URL을 입력하면 음성을 텍스트로 변환합니다")
    print("=" * 60)

    # 모델 및 언어 선택
    model_name = select_model()
    language = select_language()

    while True:
        print(f"\n{'─' * 60}")
        print(f"  현재 설정: 모델={model_name}, 언어={language or '자동감지'}")
        print(f"  종료: q | 설정 변경: s")
        print(f"{'─' * 60}")

        user_input = input("유튜브 URL 입력: ").strip()

        if user_input.lower() == 'q':
            print("\n프로그램을 종료합니다.")
            break
        elif user_input.lower() == 's':
            model_name = select_model()
            language = select_language()
            continue
        elif user_input:
            process_url(user_input, model_name, language)
        else:
            print("URL을 입력해 주세요.")
