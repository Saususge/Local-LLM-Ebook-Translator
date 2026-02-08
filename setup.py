import os
import nltk
import sys
from PyInstaller.__main__ import run

# Download NLTK data (for packaging)
nltk.download('punkt')

# Check the path of downloaded NLTK data
# First check AppData/Roaming path
nltk_data_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'nltk_data')

# Check if file exists
if not os.path.exists(os.path.join(nltk_data_path, 'tokenizers', 'punkt')):
    # If not, check second possible path
    nltk_data_path = os.path.join(os.path.expanduser('~'), 'nltk_data')
    if not os.path.exists(os.path.join(nltk_data_path, 'tokenizers', 'punkt')):
        # If still not found, download to current directory
        nltk_data_path = os.path.abspath('nltk_data')
        os.makedirs(os.path.join(nltk_data_path, 'tokenizers'), exist_ok=True)
        nltk.download('punkt', download_dir=nltk_data_path)

# PyInstaller options
pyinstaller_args = [
    'run_gui.py',                    # Main script
    '--name=LocalLLMEbookTranslator',  # Output filename
    '--onefile',                     # Package as single EXE file
    '--windowed',                    # Hide console window
    '--clean',                       # Clean temporary files
    '--hidden-import=nltk',
    '--hidden-import=nltk.tokenize',
    '--hidden-import=nltk.tokenize.punkt',
    '--hidden-import=ebooklib',
    '--hidden-import=bs4',
    '--hidden-import=pdfplumber',
    '--hidden-import=PyQt5',
    '--hidden-import=httpx',
    '--hidden-import=async_translator',

]

# Add NLTK data
if os.path.exists(os.path.join(nltk_data_path, 'tokenizers', 'punkt')):
    punkt_path = os.path.join(nltk_data_path, 'tokenizers', 'punkt')
    pyinstaller_args.append(f'--add-data={punkt_path};nltk_data/tokenizers/punkt')
    print(f"NLTK data path: {punkt_path}")
else:
    print("Warning: NLTK punkt data not found!")

# Icon-related code removed - icon file was invalid causing errors

# Run PyInstaller
print("Starting PyInstaller build...")
run(pyinstaller_args)
print("PyInstaller build completed!")
