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