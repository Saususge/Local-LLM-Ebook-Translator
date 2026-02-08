# Local-LLM-Ebook-Translator

A high-performance local Ebook translation program using Ollama. Supports EPUB and PDF files.

*Read this in other languages: [English](README.md), [한국어](README.ko.md)*

## Features

- EPUB and PDF file parsing
- Local LLM translation using Ollama (httpx + asyncio)
- **Parallel translation** for 3-8x faster performance
- Multiple language translation support
- Multilingual UI (Korean and English)
- Desktop application interface (PyQt5)
- Adjustable concurrency settings

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
   pip install -r requirements.txt
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
   - **Adjust concurrent requests** (recommended: 3-8)
   - Choose interface language (Korean/English)

3. Click the 'Start Translation' button to begin translation

## System Requirements

- Windows 10 or later (for EXE file)
- Minimum 8GB RAM (16GB or more recommended)
- Ollama-compatible system (Linux, macOS, Windows)
- GPU acceleration recommended (for faster translation)

## Performance Tips

| VRAM | Recommended Concurrent Requests |
|------|--------------------------------|
| 8GB  | 3-5 |
| 12GB | 5-8 |
| 24GB+| 8-15 |

## Notes

- Ollama must be installed separately. This program communicates with the Ollama server.
- Local LLM usage means no internet connection is required for translation.
- Translation quality depends on the model selected.
- Large files may take significant time to translate.
- The GUI application runs translation tasks in a background thread to maintain UI responsiveness.