@echo off
echo LocalLLM Ebook Translator packing start...

pip install pyinstaller
python setup.py

echo.
echo Packaging Done!
echo Find exe file in dist directory.
pause
