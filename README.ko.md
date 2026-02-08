# Local-LLM-Ebook-Translator

Ollama를 이용한 고성능 로컬 이북(Ebook) 번역 프로그램입니다. EPUB 및 PDF 파일을 지원합니다.

*다른 언어로 읽기: [English](README.md), [한국어](README.ko.md)*

## 기능

- EPUB 및 PDF 파일 파싱
- Ollama를 이용한 로컬 LLM 번역 (httpx + asyncio)
- **병렬 번역**으로 3-8배 빠른 성능
- 다양한 언어로 번역 가능
- 다국어 UI 지원 (한국어, 영어)
- 데스크톱 애플리케이션 인터페이스 (PyQt5)
- 동시 요청 수 조절 가능

## 설치 방법

### 실행 파일 다운로드 (Windows)

1. 릴리스 페이지에서 최신 버전의 `LocalLLMEbookTranslator.exe` 파일을 다운로드하세요.
2. Ollama 설치하기
   - [Ollama 다운로드 페이지](https://ollama.com/download)에서 OS에 맞는 버전을 설치하세요.
3. 원하는 언어 모델 다운로드
   ```bash
   ollama pull llama3
   ```

### 소스코드에서 설치 (개발자용)

1. 필요한 패키지 설치
   ```bash
   pip install -r requirements.txt
   ```

2. 실행 파일 빌드 (선택 사항)
   ```bash
   pip install pyinstaller
   python setup.py
   ```
   또는 Windows에서는 `build_exe.bat` 파일을 실행하세요.

## 사용 방법

### 데스크톱 애플리케이션

1. `LocalLLMEbookTranslator.exe` 파일을 실행하거나 소스 코드에서 실행할 경우:
   ```bash
   python run_gui.py
   ```

2. 애플리케이션에서 다음 설정을 구성:
   - Ollama 서버 주소 (기본: http://localhost:11434)
   - 사용할 LLM 모델 선택
   - 원본 언어 및 번역할 언어 선택
   - 입력 파일(EPUB/PDF) 및 출력 파일 선택
   - **동시 요청 수 조절** (권장: 3-8)
   - 인터페이스 언어 선택 (한국어/영어)

3. '번역 시작' 버튼을 클릭하여 번역 시작

## 시스템 요구사항

- Windows 10 이상 (EXE 파일 실행 시)
- 최소 8GB RAM (16GB 이상 권장)
- Ollama 호환 시스템 (Linux, macOS, Windows)
- GPU 가속 권장 (번역 속도 향상)

## 성능 팁

| VRAM | 권장 동시 요청 수 |
|------|-----------------|
| 8GB  | 3-5 |
| 12GB | 5-8 |
| 24GB+| 8-15 |

## 참고사항

- Ollama는 별도로 설치해야 합니다. 이 프로그램은 Ollama 서버와 통신합니다.
- 로컬에서 실행되는 LLM을 사용하므로 인터넷 연결이 필요하지 않습니다.
- 번역 품질은 선택한 모델에 따라 달라질 수 있습니다.
- 대용량 파일의 경우 번역에 시간이 많이 소요될 수 있습니다.
- GUI 애플리케이션은 번역 작업을 백그라운드 스레드에서 실행하여 UI 응답성을 유지합니다.
