import os
import nltk
import sys
from PyInstaller.__main__ import run

# NLTK 데이터 다운로드 (패키징에 포함하기 위함)
nltk.download('punkt')

# 다운로드된 NLTK 데이터 경로 확인
# 먼저 AppData/Roaming 경로 확인
nltk_data_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'nltk_data')

# 파일 존재 여부 확인
if not os.path.exists(os.path.join(nltk_data_path, 'tokenizers', 'punkt')):
    # 없으면 두 번째 가능한 경로 확인
    nltk_data_path = os.path.join(os.path.expanduser('~'), 'nltk_data')
    if not os.path.exists(os.path.join(nltk_data_path, 'tokenizers', 'punkt')):
        # 그래도 없으면 현재 디렉토리에 다운로드
        nltk_data_path = os.path.abspath('nltk_data')
        os.makedirs(os.path.join(nltk_data_path, 'tokenizers'), exist_ok=True)
        nltk.download('punkt', download_dir=nltk_data_path)

# PyInstaller 옵션
pyinstaller_args = [
    'run_gui.py',                    # 메인 스크립트
    '--name=LocalLLMEbookTranslator',  # 출력 파일명
    '--onefile',                     # 단일 EXE 파일로 패키징
    '--windowed',                    # 콘솔 창 숨기기
    '--clean',                       # 임시 파일 정리
    '--hidden-import=nltk',
    '--hidden-import=nltk.tokenize',
    '--hidden-import=nltk.tokenize.punkt',
    '--hidden-import=ebooklib',
    '--hidden-import=bs4',
    '--hidden-import=pdfplumber',
    '--hidden-import=PyQt5',
    '--hidden-import=langchain',
    '--hidden-import=langchain_ollama',
    '--hidden-import=langchain.prompts',
    '--hidden-import=langchain.chains',
    '--hidden-import=langchain_ollama',
    '--hidden-import=langchain_ollama.chat_models',

]

# NLTK 데이터 추가
if os.path.exists(os.path.join(nltk_data_path, 'tokenizers', 'punkt')):
    punkt_path = os.path.join(nltk_data_path, 'tokenizers', 'punkt')
    pyinstaller_args.append(f'--add-data={punkt_path};nltk_data/tokenizers/punkt')
    print(f"NLTK 데이터 경로: {punkt_path}")
else:
    print("경고: NLTK punkt 데이터를 찾을 수 없습니다!")

# 아이콘 관련 코드 제거 - 아이콘 파일이 유효하지 않아 오류 발생

# PyInstaller 실행
print("PyInstaller 빌드 시작...")
run(pyinstaller_args)
print("PyInstaller 빌드 완료!")
