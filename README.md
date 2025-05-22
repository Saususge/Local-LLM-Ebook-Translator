# Local-LLM-Ebook-Translator

A local Ebook translation program using Ollama and LangChain. Supports EPUB and PDF files.

*Read this in other languages: [English](README.md), [한국어](README.ko.md)*

## Features

- EPUB and PDF file parsing
- Local LLM translation using Ollama
- Multiple language translation support
- Multilingual UI (Korean and English)
- Desktop application interface (PyQt5)

## Installation

### Download Executable (Windows)

1. Download the latest `LocalLLMEbookTranslator.exe` file from the releases page.
2. Install Ollama
   - Get the appropriate version for your OS from the [Ollama download page](https://ollama.com/download).
3. Download your preferred language model
   ```bash
   ollama pull llama3
   ```

### Install from Source (For Developers)

1. Install required packages
   ```bash
   pip install langchain langchain-ollama ollama ebooklib bs4 pdfplumber nltk python-dotenv PyQt5
   ```

2. Build executable (optional)
   ```bash
   pip install pyinstaller
   python setup.py
   ```
   Or on Windows, run the `build_exe.bat` file.

## Usage

### Desktop Application

1. Run the `LocalLLMEbookTranslator.exe` file, or if running from source:
   ```bash
   python run_gui.py
   ```

2. Configure the following settings in the application:
   - Ollama server address (default: http://localhost:11434)
   - Select the LLM model to use
   - Choose source and target languages
   - Select input file (EPUB/PDF) and output file
   - Choose interface language (Korean/English)

3. Click the 'Start Translation' button to begin translation

## System Requirements

- Windows 10 or later (for EXE file)
- Minimum 8GB RAM (16GB or more recommended)
- Ollama-compatible system (Linux, macOS, Windows)
- GPU acceleration recommended (for faster translation)

## Notes

- Ollama must be installed separately. This program communicates with the Ollama server.
- Local LLM usage means no internet connection is required for translation.
- Translation quality depends on the model selected.
- Large files may take significant time to translate.
- The GUI application runs translation tasks in a background thread to maintain UI responsiveness.
- 데스크톱 애플리케이션 인터페이스 (PyQt5)

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
   pip install langchain langchain-ollama ollama ebooklib bs4 pdfplumber nltk python-dotenv PyQt5
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
   - 인터페이스 언어 선택 (한국어/영어)

3. '번역 시작' 버튼을 클릭하여 번역 시작

## 시스템 요구사항

- Windows 10 이상 (EXE 파일 실행 시)
- 최소 8GB RAM (16GB 이상 권장)
- Ollama 호환 시스템 (Linux, macOS, Windows)
- GPU 가속 권장 (번역 속도 향상)

## 참고사항

- Ollama는 별도로 설치해야 합니다. 이 프로그램은 Ollama 서버와 통신합니다.
- 로컬에서 실행되는 LLM을 사용하므로 인터넷 연결이 필요하지 않습니다.
- 번역 품질은 선택한 모델에 따라 달라질 수 있습니다.
- 대용량 파일의 경우 번역에 시간이 많이 소요될 수 있습니다.
- GUI 애플리케이션은 번역 작업을 백그라운드 스레드에서 실행하여 UI 응답성을 유지합니다.